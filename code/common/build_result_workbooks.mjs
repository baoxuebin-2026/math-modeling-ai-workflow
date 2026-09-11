/** 用结构化求解结果填充附件5副本；不重新计算优化模型。 */

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const artifactModule = path.join(
  process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,
  "@oai/artifact-tool/dist/artifact_tool.mjs",
);
const { FileBlob, SpreadsheetFile } = await import(pathToFileURL(artifactModule).href);

const root = process.cwd();
const templateDir = path.join(root, "data/raw/附件/附件5");
const outputDir = path.join(root, "data/processed/submission");
const previewDir = path.join(root, "tmp/result_workbook_previews");
const resultDir = path.join(root, "docs/results");
const processedDir = path.join(root, "data/processed");
const dates = [];
for (let stamp = Date.UTC(2025, 1, 1); stamp <= Date.UTC(2025, 11, 31); stamp += 86400000) {
  dates.push(new Date(stamp).toISOString().slice(0, 10));
}

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").trim().split(/\r?\n/);
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(header.map((name, i) => {
      const value = values[i] ?? "";
      return [name, value === "" || name === "date" ? value : Number(value)];
    }));
  });
}

async function readJson(name) {
  return JSON.parse(await fs.readFile(path.join(resultDir, name), "utf8"));
}

async function readCsv(name) {
  return parseCsv(await fs.readFile(path.join(processedDir, name), "utf8"));
}

function groupByDate(rows) {
  const grouped = new Map(dates.map((day) => [day, []]));
  for (const row of rows) grouped.get(row.date)?.push(row);
  for (const values of grouped.values()) values.sort((a, b) => a.slot - b.slot);
  return grouped;
}

function dateValue(day) {
  return new Date(`${day}T00:00:00Z`);
}

function intervalLabel(startSlot, endSlot) {
  const fmt = (minute) => minute === 1440
    ? "24:00"
    : `${Math.floor(minute / 60)}:${String(minute % 60).padStart(2, "0")}`;
  return `${fmt((startSlot - 1) * 10)}-${fmt(endSlot * 10)}`;
}

function emergencyIntervals(rows, field = "emergency_kwh") {
  const output = [];
  let start = null;
  let amount = 0;
  for (let i = 0; i < rows.length; i += 1) {
    const active = Number(rows[i][field]) > 1e-6;
    if (active && start === null) start = i + 1;
    if (active) amount += Number(rows[i][field]);
    if (start !== null && (!active || i === rows.length - 1)) {
      const end = active && i === rows.length - 1 ? i + 1 : i;
      output.push([intervalLabel(start, end), amount]);
      start = null;
      amount = 0;
    }
  }
  return output;
}

function dailyMap(items) {
  return new Map(items.map((item) => [item.date, item]));
}

function fillAnnualPlan(workbook, grouped, valueField, daily, costFn) {
  const sheet = workbook.worksheets.getItem("计划购电量");
  const matrix = dates.map((day) => {
    const rows = grouped.get(day);
    if (rows.length !== 144) throw new Error(`${day}计划购电明细不是144格`);
    const values = rows.map((row) => Number(row[valueField]));
    return [...values, values.reduce((sum, value) => sum + value, 0), costFn(daily.get(day))];
  });
  sheet.getRange("B2:EQ335").values = matrix;
  sheet.getRange("B2:EP335").format.numberFormat = "0.0000";
  sheet.getRange("EQ2:EQ335").format.numberFormat = "0.00";
}

function fillAdjustmentPlan(workbook, grouped, daily, costFn) {
  const sheet = workbook.worksheets.getItem("调整购电量");
  const matrix = dates.map((day) => {
    const rows = grouped.get(day);
    const values = rows.map((row) => Number(row.final_adjusted_kwh));
    return [...values, values.reduce((sum, value) => sum + value, 0), costFn(daily.get(day))];
  });
  sheet.getRange("B2:EQ335").values = matrix;
  sheet.getRange("B2:EP335").format.numberFormat = "0.0000";
  sheet.getRange("EQ2:EQ335").format.numberFormat = "0.00";
}

function fillChargeSheet(workbook, grouped) {
  const sheet = workbook.worksheets.getItem("充放电量");
  const values = [];
  for (const day of dates) {
    const rows = grouped.get(day);
    const first = rows[0];
    const initialSoc = Number(first.soc_end_kwh) - 0.9 * Number(first.charge_kwh)
      + Number(first.discharge_kwh) / 0.9;
    const finalSoc = Number(rows[143].soc_end_kwh);
    for (let block = 0; block < 6; block += 1) {
      const slice = rows.slice(block * 24, (block + 1) * 24);
      values.push([
        block === 0 ? dateValue(day) : null,
        `${block * 4}:00-${(block + 1) * 4}:00`,
        slice.reduce((sum, row) => sum + Number(row.charge_kwh), 0),
        slice.reduce((sum, row) => sum + Number(row.discharge_kwh), 0),
        block === 0 ? "0:00" : block === 1 ? "24:00" : null,
        block === 0 ? initialSoc : block === 1 ? finalSoc : null,
      ]);
    }
  }
  sheet.getRange(`A2:F${values.length + 1}`).values = values;
  const body = sheet.getRange(`A2:F${values.length + 1}`);
  body.format.font = { name: "Arial", size: 10 };
  body.format.verticalAlignment = "center";
  body.format.borders = { preset: "all", style: "thin", color: "#808080" };
  sheet.getRange(`A2:A${values.length + 1}`).format.numberFormat = "m/d/yy";
  sheet.getRange(`C2:D${values.length + 1}`).format.numberFormat = "0.0000";
  sheet.getRange(`F2:F${values.length + 1}`).format.numberFormat = "0.0000";
}

function fillEmergencySheet(workbook, grouped) {
  const sheet = workbook.worksheets.getItem("紧急购电量");
  const values = [];
  for (const day of dates) {
    const intervals = emergencyIntervals(grouped.get(day));
    if (intervals.length === 0) {
      values.push([dateValue(day), null, 0]);
    } else {
      intervals.forEach(([label, amount], index) => {
        values.push([index === 0 ? dateValue(day) : null, label, amount]);
      });
    }
  }
  sheet.getRange(`A2:C${values.length + 1}`).values = values;
  const body = sheet.getRange(`A2:C${values.length + 1}`);
  body.format.font = { name: "Arial", size: 10 };
  body.format.verticalAlignment = "center";
  body.format.borders = { preset: "all", style: "thin", color: "#808080" };
  sheet.getRange(`A2:A${values.length + 1}`).format.numberFormat = "m/d/yy";
  sheet.getRange(`C2:C${values.length + 1}`).format.numberFormat = "0.0000";
}

async function verifyAndExport(workbook, outputName) {
  workbook.recalculate();
  const planRange = outputName === "result1.xlsx" ? "计划购电量!A1:B8" : "计划购电量!EL1:EQ8";
  const planCheck = await workbook.inspect({
    kind: "table", range: planRange, include: "values,formulas",
    tableMaxRows: 8, tableMaxCols: 6, maxChars: 7000,
  });
  console.log(`\n${outputName} plan check\n${planCheck.ndjson}`);
  const errors = await workbook.inspect({
    kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 100 }, summary: `${outputName} formula error scan`,
  });
  console.log(errors.ndjson);
  const sheetInfo = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 5000 });
  const sheetNames = sheetInfo.ndjson.trim().split("\n").map((line) => JSON.parse(line).name);
  for (const sheetName of sheetNames) {
    const preview = await workbook.render({
      sheetName,
      range: sheetName === "计划购电量" || sheetName === "调整购电量" ? "A1:L10" : "A1:F20",
      scale: 1.2,
      format: "png",
    });
    await fs.writeFile(
      path.join(previewDir, `${outputName.replace(".xlsx", "")}_${sheetName}.png`),
      new Uint8Array(await preview.arrayBuffer()),
    );
  }
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(outputDir, outputName));
}

async function loadTemplate(name) {
  return SpreadsheetFile.importXlsx(await FileBlob.load(path.join(templateDir, name)));
}

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const q1 = await readJson("q1_results.json");
const wb1 = await loadTemplate("result1.xlsx");
wb1.worksheets.getItem("计划购电量").getRange("B2:B145").values = q1.outputs.plan_grid_kwh.map((v) => [v]);
wb1.worksheets.getItem("计划购电量").getRange("B2:B145").format.numberFormat = "0.0000";
const q1Charge = [];
for (let block = 0; block < 6; block += 1) {
  q1Charge.push([
    q1.outputs.charge_kwh.slice(block * 24, (block + 1) * 24).reduce((a, b) => a + b, 0),
    q1.outputs.discharge_kwh.slice(block * 24, (block + 1) * 24).reduce((a, b) => a + b, 0),
  ]);
}
wb1.worksheets.getItem("充放电量").getRange("B2:C7").values = q1Charge;
wb1.worksheets.getItem("充放电量").getRange("E2:E3").values = [[q1.outputs.soc_kwh[0]], [q1.outputs.soc_kwh.at(-1)]];
wb1.worksheets.getItem("充放电量").getRange("B2:C7").format.numberFormat = "0.0000";
wb1.worksheets.getItem("充放电量").getRange("E2:E3").format.numberFormat = "0.0000";
await verifyAndExport(wb1, "result1.xlsx");

const q2 = await readJson("q2_results.json");
const q2Rows = await readCsv("q2_full_detail.csv");
const q2Grouped = groupByDate(q2Rows);
const q2Daily = dailyMap(q2.daily_summary);
const wb2 = await loadTemplate("result2.xlsx");
fillAnnualPlan(wb2, q2Grouped, "plan_grid_kwh", q2Daily, (row) => row.plan_cost_cny);
fillChargeSheet(wb2, q2Grouped);
fillEmergencySheet(wb2, q2Grouped);
await verifyAndExport(wb2, "result2.xlsx");

const q3 = await readJson("q3_results.json");
const q3Rows = await readCsv("q3_full_detail.csv");
const q3Grouped = groupByDate(q3Rows);
const q3Daily = dailyMap(q3.daily_summary);
const wb3 = await loadTemplate("result3.xlsx");
fillAnnualPlan(wb3, q3Grouped, "original_plan_kwh", q3Daily, (row) => row.plan_cny);
fillAdjustmentPlan(wb3, q3Grouped, q3Daily, (row) => row.upward_cny + row.downward_cny);
fillChargeSheet(wb3, q3Grouped);
fillEmergencySheet(wb3, q3Grouped);
await verifyAndExport(wb3, "result3.xlsx");

const q4 = await readJson("q4_results.json");
const q42Rows = await readCsv("q4_2_full_detail.csv");
const q42Grouped = groupByDate(q42Rows);
const q42Daily = dailyMap(q4.q4_2.daily_summary);
const wb42 = await loadTemplate("result4-2.xlsx");
fillAnnualPlan(wb42, q42Grouped, "plan_grid_kwh", q42Daily, (row) => row.plan_cny);
fillChargeSheet(wb42, q42Grouped);
fillEmergencySheet(wb42, q42Grouped);
await verifyAndExport(wb42, "result4-2.xlsx");

const q43Rows = await readCsv("q4_3_full_detail.csv");
const q43Grouped = groupByDate(q43Rows);
const q43Daily = dailyMap(q4.q4_3.daily_summary);
const wb43 = await loadTemplate("result4-3.xlsx");
fillAnnualPlan(wb43, q43Grouped, "original_plan_kwh", q43Daily, (row) => row.plan_cny);
fillAdjustmentPlan(wb43, q43Grouped, q43Daily, (row) => row.upward_cny + row.downward_cny);
fillChargeSheet(wb43, q43Grouped);
fillEmergencySheet(wb43, q43Grouped);
await verifyAndExport(wb43, "result4-3.xlsx");

console.log(`saved 5 workbooks to ${path.relative(root, outputDir)}`);
