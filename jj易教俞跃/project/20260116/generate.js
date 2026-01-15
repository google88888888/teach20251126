const fs = require('fs');
const path = require('path');

const txtDir = path.resolve(__dirname, 'txt');
const outputFile = path.resolve(__dirname, 'output.ts');

const files = fs.readdirSync(txtDir);

let tsObjectBody = '';

files.forEach(file => {
  if (file.endsWith('.txt')) {
    const filePath = path.join(txtDir, file);
    let content = fs.readFileSync(filePath, 'utf-8');

    const key = path.basename(file, '.txt');

    // ⚠️ 处理反引号，防止破坏 ts 文件
    content = content.replace(/`/g, '\\`');

    tsObjectBody += `${JSON.stringify(key)}:\`\n${content}\n\`,\n`;
  }
});

const tsContent = `
// ⚠️ 此文件由脚本自动生成，请勿手动修改
const data: Record<string, string> = {
${tsObjectBody}
};

export default data;
`;

fs.writeFileSync(outputFile, tsContent, 'utf-8');

console.log('output.ts 生成完成 ✅');
