const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.company = "ai-skills";
pptx.subject = "AI 协作课程";
pptx.title = "AI 如何应用：从工具到 Agent，我们正在进入怎样的人机协作时代";
pptx.lang = "zh-CN";

const OUT = "docs/ai-collaboration-course-2026/generated/ai-collaboration-course-2026.pptx";

const C = {
  ink: "18212F",
  inkSoft: "445268",
  navy: "1E2A44",
  teal: "0E7490",
  mint: "B8F2E6",
  sand: "F6F1E8",
  coral: "F26B5B",
  gold: "F2C14E",
  slate: "6B7280",
  line: "D6DCE5",
  white: "FFFFFF",
  fog: "EEF3F8",
  success: "2C7A5C",
};

const FONT = {
  title: "Microsoft YaHei",
  body: "Microsoft YaHei",
  accent: "Georgia",
};

function addPageNumber(slide, n) {
  slide.addText(String(n), {
    x: 9.15, y: 5.08, w: 0.35, h: 0.2,
    fontFace: FONT.accent, fontSize: 10, italic: true, color: C.slate,
    align: "right", margin: 0,
  });
}

function addFooter(slide, label) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.0, y: 5.18, w: 10, h: 0.45,
    line: { color: C.white, transparency: 100 },
    fill: { color: C.white },
  });
  slide.addText(label, {
    x: 0.55, y: 5.28, w: 5.5, h: 0.12,
    fontFace: FONT.body, fontSize: 9, color: C.slate, margin: 0,
  });
}

function addHeader(slide, title, kicker, n, dark = false) {
  const bg = dark ? C.navy : C.white;
  slide.background = { color: bg };
  if (!dark) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 10, h: 0.55,
      line: { color: C.teal, transparency: 100 },
      fill: { color: C.teal },
    });
  }
  slide.addText(kicker, {
    x: 0.58, y: dark ? 0.52 : 0.76, w: 2.2, h: 0.2,
    fontFace: FONT.accent, fontSize: 12, italic: true,
    color: dark ? C.mint : C.teal, margin: 0, charSpacing: 1,
  });
  slide.addText(title, {
    x: 0.58, y: dark ? 0.82 : 1.02, w: 8.5, h: 0.58,
    fontFace: FONT.title, fontSize: 24, bold: true,
    color: dark ? C.white : C.ink, margin: 0,
  });
  addPageNumber(slide, n);
}

function addBulletList(slide, items, x, y, w, h, opts = {}) {
  const runs = [];
  items.forEach((item, i) => {
    runs.push({
      text: item,
      options: { bullet: true, breakLine: i < items.length - 1 },
    });
  });
  slide.addText(runs, {
    x, y, w, h,
    fontFace: opts.fontFace || FONT.body,
    fontSize: opts.fontSize || 15,
    color: opts.color || C.ink,
    breakLine: false,
    valign: "top",
    margin: opts.margin ?? 0.08,
    paraSpaceAfterPt: 8,
  });
}

function addCard(slide, { x, y, w, h, title, body, accent, dark = false, titleSize = 18, bodySize = 13 }) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    line: { color: dark ? accent : C.line, width: dark ? 1.6 : 1 },
    fill: { color: dark ? C.navy : C.white },
    shadow: { type: "outer", color: "000000", blur: 2, offset: 1, angle: 45, opacity: 0.1 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: x + 0.18, y: y + 0.2, w: 0.12, h: h - 0.4,
    line: { color: accent, transparency: 100 },
    fill: { color: accent },
  });
  slide.addText(title, {
    x: x + 0.4, y: y + 0.18, w: w - 0.6, h: 0.35,
    fontFace: FONT.title, fontSize: titleSize, bold: true,
    color: dark ? C.white : C.ink, margin: 0,
  });
  slide.addText(body, {
    x: x + 0.4, y: y + 0.6, w: w - 0.6, h: h - 0.8,
    fontFace: FONT.body, fontSize: bodySize,
    color: dark ? "E8EEF5" : C.inkSoft, margin: 0,
    valign: "top",
  });
}

function cover() {
  const slide = pptx.addSlide();
  slide.background = { color: C.navy };

  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 10, h: 5.625,
    line: { color: C.navy, transparency: 100 },
    fill: { color: C.navy },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 6.3, y: 0, w: 3.7, h: 5.625,
    line: { color: C.teal, transparency: 100 },
    fill: { color: C.teal, transparency: 10 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 6.95, y: 0.55, w: 2.1, h: 2.1,
    line: { color: C.gold, transparency: 100 },
    fill: { color: C.gold, transparency: 18 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 7.3, y: 2.05, w: 1.45, h: 1.45,
    line: { color: C.coral, transparency: 100 },
    fill: { color: C.coral, transparency: 16 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.62, y: 0.72, w: 1.1, h: 0.1,
    line: { color: C.mint, transparency: 100 },
    fill: { color: C.mint },
  });

  slide.addText("AI 如何应用", {
    x: 0.72, y: 1.15, w: 4.2, h: 0.6,
    fontFace: FONT.title, fontSize: 28, bold: true,
    color: C.white, margin: 0,
  });
  slide.addText("从工具到 Agent，我们正在进入怎样的人机协作时代", {
    x: 0.72, y: 1.8, w: 5.45, h: 0.95,
    fontFace: FONT.title, fontSize: 24, bold: true,
    color: C.white, margin: 0,
  });
  slide.addText("从 GTC 2026、个人工作辅助到 Agent 协作范式升级", {
    x: 0.72, y: 2.92, w: 4.9, h: 0.3,
    fontFace: FONT.accent, fontSize: 13, italic: true,
    color: C.mint, margin: 0,
  });
  slide.addText("这不是一场关于提示词的课，而是一场关于工作重构的课。", {
    x: 0.72, y: 3.5, w: 4.8, h: 0.55,
    fontFace: FONT.body, fontSize: 17,
    color: "E8EEF5", margin: 0,
  });

  addCard(slide, {
    x: 6.05, y: 3.56, w: 3.15, h: 1.22,
    title: "课程主线",
    body: "故事开场\n行业现状\n个人价值\nAgent 方法\n协作分级\n行动建议",
    accent: C.gold,
    dark: true,
    titleSize: 18,
    bodySize: 13,
  });

  slide.addText("AI Collaboration Course 2026", {
    x: 0.72, y: 5.08, w: 3.2, h: 0.18,
    fontFace: FONT.accent, fontSize: 10, italic: true, color: C.slate, margin: 0,
  });
  addPageNumber(slide, 1);
}

function storySlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "AI 正在改变的，不只是效率，而是工作单元", "Changing Unit Of Work", 2);

  addCard(slide, {
    x: 0.58, y: 1.62, w: 4.1, h: 2.75,
    title: "过去：人独立完成任务",
    body: "1. 自己找资料\n2. 自己整理问题\n3. 自己写方案\n4. 自己执行\n5. 自己检查结果",
    accent: C.coral,
  });
  addCard(slide, {
    x: 5.1, y: 1.62, w: 4.32, h: 2.75,
    title: "现在：人 + AI + 系统并行协作",
    body: "1. 人定义目标和边界\n2. AI 并行铺开资料、方案和初稿\n3. AI 调工具完成部分执行\n4. 系统以测试与规则做验证\n5. 人负责判断、取舍、签字与兜底",
    accent: C.teal,
  });
  slide.addShape(pptx.ShapeType.chevron, {
    x: 4.55, y: 2.52, w: 0.5, h: 0.55,
    line: { color: C.gold, transparency: 100 },
    fill: { color: C.gold },
  });
  slide.addText("从单线程执行\n转向编排式协作", {
    x: 3.95, y: 3.22, w: 1.7, h: 0.55,
    fontFace: FONT.body, fontSize: 13, color: C.inkSoft, bold: true,
    align: "center", margin: 0,
  });
  slide.addText("以前我们是自己完成任务；现在越来越像是在指挥一个带工具的数字同事。", {
    x: 0.58, y: 4.6, w: 8.4, h: 0.3,
    fontFace: FONT.accent, fontSize: 16, italic: true, color: C.teal, margin: 0,
  });
  addFooter(slide, "先建立代入感，再引入方法论。");
}

function whyNowSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "为什么 2025-2026 是重新理解 AI 的时间点", "Why Now", 3);

  const signals = [
    ["算力与基础设施继续推进", "AI 不是短期热点，而是持续投资的基础能力。"],
    ["Agent 成为共同语言", "行业关注点从模型本身转向任务完成和系统落地。"],
    ["标杆工具开始后台执行", "Background Agent、多智能体协作不再只是 demo。"],
    ["AI 进入真实业务工作流", "从会说，转向会接系统、会验证、会交付。"],
  ];

  signals.forEach((s, i) => {
    const x = 0.58 + (i % 2) * 4.46;
    const y = 1.6 + Math.floor(i / 2) * 1.45;
    addCard(slide, {
      x, y, w: 4.06, h: 1.12,
      title: `信号 ${i + 1}  ${s[0]}`,
      body: s[1],
      accent: [C.teal, C.coral, C.gold, C.success][i],
      titleSize: 16,
      bodySize: 12,
    });
  });

  slide.addText("2023 年大家问的是 AI 能不能用，2024 年问的是怎么接入，2025 年开始问的是怎样把它嵌入生产流程。", {
    x: 0.58, y: 4.72, w: 8.7, h: 0.38,
    fontFace: FONT.accent, fontSize: 14, italic: true, color: C.coral, margin: 0,
  });
  addFooter(slide, "重点不是某个产品，而是行业重心从“能力展示”转向“系统落地”。");
}

function threeLayersSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "AI 改变的，不只是工具，而是工作的三层结构", "Three Layers", 4);

  const cols = [
    { title: "认知增强", body: "理解、总结、比较、推演\n适合调研、纪要、分析、方案", accent: C.teal },
    { title: "执行增强", body: "写、改、查、测、联动工具\n适合代码、文档、SQL、脚本", accent: C.coral },
    { title: "系统增强", body: "沉淀规则、复用经验、形成闭环\n适合 SOP、规则库、自动验证", accent: C.gold },
  ];
  cols.forEach((c, i) => addCard(slide, {
    x: 0.58 + i * 3.07, y: 1.72, w: 2.72, h: 2.45,
    title: c.title, body: c.body, accent: c.accent,
    titleSize: 20, bodySize: 14,
  }));

  slide.addShape(pptx.ShapeType.rect, {
    x: 0.58, y: 4.48, w: 8.78, h: 0.02,
    line: { color: C.line, transparency: 100 }, fill: { color: C.line },
  });
  slide.addText("AI 的真正价值，不只是替你产出答案，而是帮助你扩大认知半径、执行半径和系统半径。", {
    x: 0.72, y: 4.68, w: 8.2, h: 0.4,
    fontFace: FONT.title, fontSize: 18, bold: true, color: C.ink, align: "center", margin: 0,
  });
  addFooter(slide, "从“更快完成一次任务”，升级到“持续放大工作半径”。");
}

function valueSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "今天，普通人已经可以从 AI 获得什么", "Immediate Value", 5);

  const cards = [
    { title: "信息处理", body: "摘要、搜索、调研、整理知识", accent: C.teal },
    { title: "内容生产", body: "方案、邮件、汇报、PPT、大纲", accent: C.coral },
    { title: "专业工作", body: "代码、测试、分析、脚本、数据处理", accent: C.gold },
    { title: "决策支持", body: "列方案、找风险、做预演、补盲区", accent: C.success },
  ];
  cards.forEach((c, i) => {
    const x = 0.58 + (i % 2) * 4.46;
    const y = 1.68 + Math.floor(i / 2) * 1.45;
    addCard(slide, {
      x, y, w: 4.06, h: 1.1,
      title: c.title, body: c.body, accent: c.accent,
      titleSize: 18, bodySize: 13,
    });
  });
  slide.addText("AI 最有价值的地方，往往不是替你做最后决策，而是快速铺开可能性空间。", {
    x: 0.58, y: 4.72, w: 8.5, h: 0.35,
    fontFace: FONT.accent, fontSize: 15, italic: true, color: C.teal, margin: 0,
  });
  addFooter(slide, "这一页用来拉近与非技术听众的距离。");
}

function agentSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "从 AI 工具到 Agent：差别到底在哪里", "Tool To Agent", 6);

  addCard(slide, {
    x: 0.58, y: 1.62, w: 2.76, h: 2.2,
    title: "工具",
    body: "会回答\n擅长问答、生成、总结",
    accent: C.line,
    titleSize: 22,
  });
  addCard(slide, {
    x: 3.62, y: 1.62, w: 2.76, h: 2.2,
    title: "Copilot",
    body: "会陪你完成当前任务\n围绕具体界面持续协助",
    accent: C.coral,
    titleSize: 22,
  });
  addCard(slide, {
    x: 6.66, y: 1.62, w: 2.76, h: 2.2,
    title: "Agent",
    body: "有目标、有工具、有反馈\n持续执行直到达到标准",
    accent: C.teal,
    titleSize: 22,
  });

  addBulletList(slide, [
    "LLM 解决的是“会不会想”",
    "Agent 解决的是“能不能做完”",
    "真正能落地的 Agent 依赖验证层，而不靠一句神奇 prompt",
  ], 0.9, 4.18, 8.2, 0.75, { fontSize: 15, color: C.ink });

  addFooter(slide, "边界提醒：从“管理人的容错”转向“管理机器的幻觉”。");
}

function levelsSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "我们和 AI 协作，正在从“会用”走向“会设计系统”", "8 Levels", 7);

  const levels = [
    "1 问答调用", "2 自动补全", "3 上下文工程", "4 复利工程",
    "5 能力扩展", "6 反馈闭环", "7 后台执行", "8 Agent 团队",
  ];
  levels.forEach((level, i) => {
    const x = 0.58 + (i % 4) * 2.28;
    const y = 1.7 + Math.floor(i / 4) * 1.24;
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y, w: 2.02, h: 0.82, rectRadius: 0.08,
      line: { color: i < 2 ? C.line : i < 5 ? C.teal : C.coral, width: 1.2 },
      fill: { color: i < 2 ? C.fog : i < 5 ? "EAF7FA" : "FFF1EE" },
    });
    slide.addText(level, {
      x: x + 0.14, y: y + 0.2, w: 1.72, h: 0.2,
      fontFace: FONT.title, fontSize: 16, bold: true, color: C.ink, margin: 0,
    });
  });

  addCard(slide, {
    x: 0.58, y: 4.12, w: 2.66, h: 0.86,
    title: "大多数人还停在",
    body: "Level 1-2：把 AI 当搜索和写作助手",
    accent: C.line,
    titleSize: 15, bodySize: 12,
  });
  addCard(slide, {
    x: 3.5, y: 4.12, w: 2.86, h: 0.86,
    title: "真正拉开差距的是",
    body: "Level 3-5：上下文、规则沉淀、工具连接",
    accent: C.teal,
    titleSize: 15, bodySize: 12,
  });
  addCard(slide, {
    x: 6.62, y: 4.12, w: 2.8, h: 0.86,
    title: "接近组织能力的是",
    body: "Level 6-8：反馈闭环、后台执行、多 Agent 协作",
    accent: C.coral,
    titleSize: 15, bodySize: 12,
  });
  addFooter(slide, "真正的复利来自把经验和坑沉淀成规则，而不是一次次手动纠错。");
}

function constraintSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "高级协作不是给步骤，而是定义边界", "Constraint > Instruction", 8);

  addCard(slide, {
    x: 0.58, y: 1.64, w: 4.08, h: 2.45,
    title: "传统指令：长且脆弱",
    body: "“请帮我写一个登录接口，要连接 MySQL，密码要加密，查不到用户要返回 404，记得写注释……”",
    accent: C.coral,
    titleSize: 20, bodySize: 14,
  });
  addCard(slide, {
    x: 5.02, y: 1.64, w: 4.4, h: 2.45,
    title: "高级约束：短且稳健",
    body: "目标：实现登录接口。\n约束：遵循现有 ErrorHandler；数据库必须走现有 ORM；必须有边界条件测试；测试通过前不要停止重试。",
    accent: C.teal,
    titleSize: 20, bodySize: 14,
  });

  addBulletList(slide, [
    "可使用什么工具",
    "不可修改什么内容",
    "什么标准算完成",
    "失败后如何处理",
    "何时必须人工确认",
  ], 0.74, 4.34, 3.0, 0.72, { fontSize: 14, color: C.ink });

  slide.addText("约束优于指令。", {
    x: 4.05, y: 4.48, w: 1.95, h: 0.25,
    fontFace: FONT.title, fontSize: 22, bold: true, color: C.coral, margin: 0,
    align: "center",
  });
  slide.addText("不要试图训练一个完美的灵魂，要试图构建一个无懈可击的规则笼子。", {
    x: 5.55, y: 4.38, w: 3.7, h: 0.42,
    fontFace: FONT.accent, fontSize: 13, italic: true, color: C.inkSoft, margin: 0,
  });
  addFooter(slide, "步骤会过时，但约束能适配变化。");
}

function infraSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "Agent 能否落地，取决于三件基础设施", "Infrastructure", 9);

  const infra = [
    { title: "上下文工程", body: "决定模型看什么。\n不是给更多内容，而是给更高信号的内容。", accent: C.teal },
    { title: "MCP / 工具接入", body: "决定 AI 能不能连接真实系统。\n让模型从“会说”变成“会拿数据、会调用能力”。", accent: C.coral },
    { title: "反馈闭环 / 验证层", body: "决定 Agent 能否发现错误并继续修正。\nCI、测试、安全扫描都是护栏。", accent: C.gold },
  ];
  infra.forEach((item, i) => addCard(slide, {
    x: 0.58 + i * 3.07, y: 1.74, w: 2.74, h: 2.7,
    title: item.title, body: item.body, accent: item.accent,
    titleSize: 20, bodySize: 14,
  }));

  slide.addText("能不能真正把 AI 用进工作流，核心不是模型多强，而是上下文、接口和验证是否完善。", {
    x: 0.72, y: 4.74, w: 8.35, h: 0.36,
    fontFace: FONT.accent, fontSize: 15, italic: true, color: C.teal, margin: 0,
  });
  addFooter(slide, "从 demo 变成生产力，靠的是系统工程。");
}

function trendsSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "接下来真正会发生什么", "Next 1-2 Years", 10);

  addBulletList(slide, [
    "AI 会继续从聊天窗口进入业务流程",
    "每个人都会逐步拥有自己的数字副驾和后台 Agent",
    "大量岗位不会立刻消失，但工作内容会被重新切分",
    "会使用 AI 的人很多，但会设计协作系统的人稀缺",
    "组织竞争力会越来越取决于人机协作质量",
  ], 0.72, 1.72, 5.3, 2.55, { fontSize: 16 });

  addCard(slide, {
    x: 6.2, y: 1.72, w: 3.15, h: 2.6,
    title: "关键能力迁移",
    body: "未来重要的能力之一，不是亲自做完所有事，而是能定义目标、配置系统、验证结果。",
    accent: C.coral,
    titleSize: 20, bodySize: 15,
  });
  addFooter(slide, "趋势判断的落点，不是焦虑，而是能力重心的变化。");
}

function actionSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, "我们现在应该怎么开始", "Action", 11, true);

  const actions = [
    "先从日常高频工作切入，而不是追求一步到位的全自动",
    "沉淀规则库：不只是改结果，更要改背后的规则文件和提示词",
    "尽早接触工具调用、MCP 和自动验证机制",
    "用“小闭环”训练团队协作范式，再逐步升级到后台 Agent",
  ];

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.62, y: 1.52, w: 5.5, h: 2.95, rectRadius: 0.08,
    line: { color: C.mint, width: 1.4 },
    fill: { color: "17314A" },
  });
  addBulletList(slide, actions, 0.9, 1.88, 4.95, 2.35, {
    fontSize: 16, color: C.white, margin: 0.08,
  });

  addCard(slide, {
    x: 6.45, y: 1.56, w: 2.9, h: 2.9,
    title: "收束金句",
    body: "AI 不先替代岗位，它先替代低杠杆工作。\n\n人与 AI 的差距，不在会不会用，而在会不会设计协作。\n\n从工具到 Agent，真正变化的是工作的组织方式。",
    accent: C.gold,
    dark: true,
    titleSize: 20,
    bodySize: 14,
  });
  slide.addText("未来重要的能力，不只是亲自做完所有事，而是定义目标、约束系统、验证结果。", {
    x: 0.64, y: 4.78, w: 8.7, h: 0.34,
    fontFace: FONT.accent, fontSize: 15, italic: true, color: C.mint, margin: 0,
  });
  addFooter(slide, "结束页建议留出问答空间。");
}

async function main() {
  cover();
  storySlide();
  whyNowSlide();
  threeLayersSlide();
  valueSlide();
  agentSlide();
  levelsSlide();
  constraintSlide();
  infraSlide();
  trendsSlide();
  actionSlide();

  pptx.theme = {
    headFontFace: FONT.title,
    bodyFontFace: FONT.body,
    lang: "zh-CN",
  };

  await pptx.writeFile({ fileName: OUT });
  console.log(`Wrote ${OUT}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
