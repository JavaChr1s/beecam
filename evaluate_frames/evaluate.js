const fs = require("fs").promises;
const writeXlsxFile = require("write-excel-file/node");
const path = require("path");

if (process.argv.length === 2) {
  console.error(
    "Missing <dir> argument!\nUsage: node evaluate.js <dir> [<addSumRow>][<minDiff in seconds>]"
  );
  process.exit(1);
}
const dir = process.argv[2];
const addSumRow = process.argv.length === 4 ? process.argv[3] === 'true' : false;
const minDiff = process.argv.length === 5 ? parseInt(process.argv[4]) : 60;

const ATTRIBUTE_SUFFIX = '.txt';

const allCategories = new Set();
const allAttributes = new Set();

const writeExcel = async (data, filePath) => {
  await writeXlsxFile(data, {
    schema: [
      {
        column: "Datum",
        type: Date,
        format: "dd.mm.yyyy",
        value: (item) => item.date,
      },
      {
        column: "Uhrzeit",
        type: Date,
        format: "hh:mm:ss",
        value: (item) => item.date,
      },
      {
        column: "Cam",
        type: String,
        value: (item) => item.cam,
      },
      ...[...allAttributes]
        .sort()
        .map((attribute) => ({
          column: attribute,
          type: String,
          value: (item) => item[attribute],
        })),
      ...[...allCategories]
        .filter((category) => category !== "false")
        .sort()
        .map((category) => ({
          column: category,
          type: Number,
          value: (item) => item[category],
        })),
      {
        column: "In x Dateien gefunden",
        type: Number,
        value: (item) => item.foundInFiles,
      },
      {
        column: "Zuletzt gesehen",
        type: Date,
        format: "dd.mm.yyyy hh:mm:ss",
        width: 20,
        value: (item) => item.lastFound,
      },
    ],
    filePath,
  });
  console.log("Wrote xlsx file", filePath);
};

const evaluateCategory = async (camDir, cam, day, category, camAttributes) => {
  const categoryDir = path.join(camDir, category);

  const [ items, categoryAttributes ] = await getSubDirectories(categoryDir, camAttributes);
  let previousReadItem;
  let previousWrittenItem;
  const itemDatas = items
    .map((item) => {
      const itemDir = path.join(categoryDir, item);
      const split = item.split("__");
      let dateString;
      let timeString;
      if (item.indexOf("__") > -1) {
        dateString = split[0].split("-");
        timeString = split[1].split("-");
      } else if (item.indexOf('-') > -1) {
        dateString = day.split("-");
        timeString = item.split("-");
      } else {
        return null;
      }
      const date = new Date(
        dateString[0],
        dateString[1] - 1,
        dateString[2],
        timeString[0],
        timeString[1],
        timeString[2]
      )
      date.setTime(date.getTime() - date.getTimezoneOffset() * 60 * 1000 );
      return {
        itemDir,
        date,
        cam,
        category,
        [category]: 1,
        ...categoryAttributes,
      };
    })
    .filter((item) => !!item)
    .filter((item) => !item['false'])
    .filter((item) => {
      if (!previousReadItem) {
        previousReadItem = item;
        previousWrittenItem = item;
        return true;
      }

      const previousDate = previousReadItem.date;
      const diff = (item.date - previousDate) / 1000;
      const isSameItem = diff <= minDiff;
      if (isSameItem) {
        previousWrittenItem.foundInFiles =
          (previousWrittenItem.foundInFiles || 1) + 1;
        previousWrittenItem.lastFound = item.date;
      } else {
        previousWrittenItem = item;
      }
      previousReadItem = item;
      return !isSameItem;
    });
  return await Promise.all(
    itemDatas
      .map(async (itemData) => {
        const itemFrames = await fs.readdir(itemData.itemDir, { withFileTypes: true })
        const itemAttributes = readAttributes(itemFrames);
        return {
          ...itemData,
          ...itemAttributes,
        };
      })
  );
};

const evaluateCam = async (dayDir, day, cam, dayAttributes) => {
  const camDir = path.join(dayDir, cam);

  const [ categories, camAttributes ] = await getSubDirectories(camDir, dayAttributes);
  categories.forEach((category) => allCategories.add(category));

  return [
      (await Promise.all(categories.map((category) => evaluateCategory(camDir, cam, day, category, camAttributes))))
        .flat()
        .sort((item1, item2) => item1.date - item2.date),
      camAttributes,
  ];
};

const evaluateDay = async (monthDir, day, monthAttributes) => {
  const dayDir = path.join(monthDir, day);

  const [ cams, dayAttributes ] = await getSubDirectories(dayDir, monthAttributes);
  const dayData = (
    await Promise.all(
      cams
        .sort(
          (cam1, cam2) =>
            parseInt(cam1.split("-")[1]) - parseInt(cam2.split("-")[1])
        )
        .map(async (cam) => {
          const [ camData, camAttributes ] = await evaluateCam(dayDir, day, cam, dayAttributes);
          return [
            ...camData,
            // add sum line between cams
            ...(addSumRow ? [{
              date: camData.length ? camData[0].date : undefined,
              ...camAttributes,
              ...[...allCategories].reduce((line, category) =>
                ({
                  ...line,
                  [category]:
                    camData.map((item) => item[category])
                      .reduce((sum, value) => value ? sum + value : sum, 0) || undefined
                }),
              {}),
            }] : [])
          ]
        })
    )
  ).flat();
  await writeExcel(dayData, `./${day.split('_')[0]}.xlsx`);
  return dayData;
};

const evaluateMonth = async (month, attributes) => {
  const filePath = `./${month}.xlsx`;
  const monthDir = path.join(dir, month);

  const [ days, monthAttributes ] = await getSubDirectories(monthDir, attributes);
  const monthData = (
    await Promise.all(days.map((day) => evaluateDay(monthDir, day, monthAttributes)))
  ).flat();

  await writeExcel(monthData, filePath);
  return monthData;
};

const getSubDirectories = async (dir, attributes) => {
  const files = await fs.readdir(dir, { withFileTypes: true });
  return [
    files
      .filter((file) => file.isDirectory())
      .map((file) => file.name)
      .sort(),
    {
      ...attributes,
      ...readAttributes(files),
    }
  ];
};

const readAttributes = (files) => {
  const attributes = {};
  files
    .filter((file) => !file.isDirectory())
    .filter((file) => file.name.endsWith(ATTRIBUTE_SUFFIX))
    .map((file) => {
      const [ key, value ] = file.name.split('_');
      if (key && value && value.includes(ATTRIBUTE_SUFFIX)) {
        attributes[key] = value.split(ATTRIBUTE_SUFFIX)[0];
        allAttributes.add(key);
      }
    });
  return attributes;
}

(async () => {
  console.log("Evaluating dir ", dir);

  const [ months, attributes ] = await getSubDirectories(dir, {});
  console.log("Months:", months);

  const monthData = await Promise.all(months.map((month) => evaluateMonth(month, attributes)));
  
  const dirSplit = dir.split("/");
  await writeExcel(monthData.flat(), "./" + dirSplit[dirSplit.length - 1] + ".xlsx");
})();
