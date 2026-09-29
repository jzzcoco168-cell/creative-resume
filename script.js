/*
  这里故意只保留“交互”。
  所有作品名称、说明、图片位置都写在 index.html 里，
  以后你只需要换图片，不需要看懂 JS。
*/

const projects = {
  cctv: {
    type: "01 / TV · NEW MEDIA",
    title: "《谁知盘中餐》",
    description: "CCTV-17 农业农村频道项目。参与节目策划、外景拍摄统筹、新媒体运营及采访视频制作。这里可以放节目链接或视频链接。",
    links: [
      ["节目链接", "https://tv.cctv.com/2023/05/11/VIDEcIiP0PsH5gxEQ4cPfKfO230511.shtml"],
      ["关闭", "#close"]
    ]
  },

  wechat: {
    type: "02 / EDITORIAL · WECHAT",
    title: "央视三农公众号",
    description: "《“声”动早餐》第二季。将电视节目内容转化为适合微信公众号传播的图文内容。这里可以放具体公众号文章链接。",
    links: [
      ["公众号文章", "https://mp.weixin.qq.com/s/n9GxOhwT2aeSL522StRu4A"],
      ["关闭", "#close"]
    ]
  },

  "8300": {
    type: "03 / SHORT FILM",
    title: "《8300》",
    description: "微电影作品。这里可以放完整影片、剧照或项目介绍链接。",
    links: [
      ["观看影片", "https://www.bilibili.com/video/BV1fr2dYLExa/?spm_id_from=333.1387.homepage.video_card.click&vd_source=6ad3f7cc88e89e03c734cf5c3399fa5d"],
      ["关闭", "#close"]
    ]
  },

  campus: {
    type: "04 / VIDEO PRODUCTION",
    title: "校园晚会宣传片",
    description: "本科时期学生社团联合会参与制作的校园晚会宣传片。这里可以放成片链接。",
    links: [
      ["观看宣传片", "https://www.bilibili.com/video/BV1aJ411Y73U/?spm_id_from=333.337.search-card.all.click&vd_source=6ad3f7cc88e89e03c734cf5c3399fa5d"],
      ["关闭", "#close"]
    ]
  },

  story: {
    type: "05 / STORY / IP",
    title: "电影故事项目设想",
    description: "备考阶段完成的电影故事项目设想。这里可以放 PDF、在线文档或项目图片。",
    links: [
      ["打开项目设想", "#"],
      ["关闭", "#close"]
    ]
  },

  outline: {
    type: "06 / STORY / DEVELOPMENT",
    title: "电影项目大纲",
    description: "电影项目大纲与开发材料。与上一项分开呈现，方便分别放置两份文档或两组图片。",
    links: [
      ["打开项目大纲", "#"],
      ["关闭", "#close"]
    ]
  },

  f1: {
    type: "07 / DATA / WEB",
    title: "The Path to the Top of F1 and Opportunities in China",
    description: "研究生时期的数据可视化新闻项目，使用 Tableau 完成数据可视化，并负责网页视觉与页面设计。",
    links: [
      ["OPEN PROJECT", "https://jzzcoco168-cell.github.io/The-path-to-the-top-of-F1-and-Opportunities-in-China/"],
      ["关闭", "#close"]
    ]
  },

  ddl: {
    type: "08 / PYTHON / GAME",
    title: "《DDL 终极防御战》",
    description: "研究生时期 Python / Pygame 游戏项目。独立完成全部代码，并负责视觉与音效素材整合。",
    links: [
      ["查看项目", "videos/录屏+24db.mp4"],
      ["关闭", "#close"]
    ]
  }
};

const modal = document.getElementById("projectModal");
const modalType = document.getElementById("modalType");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalButtons = document.getElementById("modalButtons");

function openProject(id) {
  const project = projects[id];
  if (!project) return;

  modalType.textContent = project.type;
  modalTitle.textContent = project.title;
  modalDescription.textContent = project.description;
  modalButtons.innerHTML = "";

  project.links.forEach(([text, href]) => {
    const link = document.createElement("a");
    link.textContent = text;
    link.href = href;

    if (href.startsWith("http")) {
      link.target = "_blank";
      link.rel = "noopener";
    }

    if (href === "#close") {
      link.addEventListener("click", function(e) {
        e.preventDefault();
        closeProject();
      });
    }

    if (href === "#") {
      link.addEventListener("click", function(e) {
        e.preventDefault();
        alert("这里换成你的真实作品链接即可。");
      });
    }

    modalButtons.appendChild(link);
  });

  modal.classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeProject() {
  modal.classList.remove("open");
  document.body.style.overflow = "";
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") closeProject();
});
