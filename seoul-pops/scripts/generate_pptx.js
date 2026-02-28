const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const pres = new pptxgen();
pres.title = "서울 생활인구 EDA";

// Title Slide
let slide = pres.addSlide();
slide.addText("서울 생활인구 데이터 탐색적 분석 (EDA)", {
    x: 1, y: 1.5, w: '80%', h: 1,
    fontSize: 32, bold: true, align: 'center', color: '363636'
});
slide.addText("2026년 01월 데이터 기준", {
    x: 1, y: 3.5, w: '80%', h: 0.5,
    fontSize: 18, align: 'center', color: '7F7F7F'
});

// 1. Data Summary
slide = pres.addSlide();
slide.addText("1. 데이터 포맷 및 효율성", { x: 0.5, y: 0.5, fontSize: 24, bold: true });
slide.addText([
    { text: "CSV 크기: 613 MB\n", options: { fontSize: 18 } },
    { text: "Parquet 크기: 129 MB\n", options: { fontSize: 18 } },
    { text: "효율성: 약 79% 공간 절약 달성", options: { fontSize: 18, bold: true, color: '008000' } }
], { x: 0.5, y: 1.5, w: 8 });

// 2. Top 10 Gu
slide = pres.addSlide();
slide.addText("2. 구별 생활인구 상위 10개", { x: 0.5, y: 0.5, fontSize: 24, bold: true });
if (fs.existsSync('docs/images/top_10_gu.png')) {
    slide.addImage({ path: 'docs/images/top_10_gu.png', x: 0.5, y: 1.0, w: 9, h: 4.5 });
}
slide.addText("Insight: 강남, 송파, 서초 등 강남 3구가 압도적으로 높은 생활인구를 기록함", { x: 0.5, y: 5.6, w: 9, fontSize: 14, italic: true });

// 3. Top 15 Dong
slide = pres.addSlide();
slide.addText("3. 행정동별 생활인구 상위 15개", { x: 0.5, y: 0.5, fontSize: 24, bold: true });
if (fs.existsSync('docs/images/top_15_dong.png')) {
    slide.addImage({ path: 'docs/images/top_15_dong.png', x: 0.5, y: 1.0, w: 9, h: 4.5 });
}
slide.addText("Insight: 역삼1동과 여의동이 비즈니스 중심지로서 독보적인 1, 2위 차지", { x: 0.5, y: 5.6, w: 9, fontSize: 14, italic: true });

// 4. Hourly Trend
slide = pres.addSlide();
slide.addText("4. 서울시 전체 시간대별 흐름", { x: 0.5, y: 0.5, fontSize: 24, bold: true });
if (fs.existsSync('docs/images/hourly_trend.png')) {
    slide.addImage({ path: 'docs/images/hourly_trend.png', x: 0.5, y: 1.0, w: 9, h: 4.5 });
}

slide = pres.addSlide();
slide.addText("4-2. 주요 구/동 시간대별 비교", { x: 0.5, y: 0.3, fontSize: 24, bold: true });
if (fs.existsSync('docs/images/hourly_trend_top_gu.png')) {
    slide.addImage({ path: 'docs/images/hourly_trend_top_gu.png', x: 0.2, y: 1.0, w: 4.6, h: 3.5 });
}
if (fs.existsSync('docs/images/hourly_trend_top_dong.png')) {
    slide.addImage({ path: 'docs/images/hourly_trend_top_dong.png', x: 5.2, y: 1.0, w: 4.6, h: 3.5 });
}
slide.addText("강남구/역삼1동 등 업무지구는 낮 시간대 피크가 뚜렷하며, 주거지역은 변동폭이 완만함", { x: 0.5, y: 5.0, w: 9, fontSize: 12 });

// 5. Age Gender
slide = pres.addSlide();
slide.addText("5. 연령 및 성별 분포", { x: 0.5, y: 0.5, fontSize: 24, bold: true });
if (fs.existsSync('docs/images/age_gender_dist.png')) {
    slide.addImage({ path: 'docs/images/age_gender_dist.png', x: 0.5, y: 1.0, w: 9, h: 4.5 });
}
slide.addText("Insight: 여성이 약 53%로 약간 더 많으며, 30대 후반 및 40대 후반의 활동량이 많음", { x: 0.5, y: 5.6, w: 9, fontSize: 14, italic: true });

// 6. Deep Dives
const targets = ["연남동", "성수1가1동", "성수1가2동", "성수2가1동", "성수2가3동", "역삼1동", "역삼2동"];
targets.forEach(dong => {
    slide = pres.addSlide();
    slide.addText(`📍 상세 분석: ${dong}`, { x: 0.5, y: 0.3, fontSize: 22, bold: true, color: '003366' });

    const linePath = `docs/images/targets/${dong}_hourly.png`;
    const heatPath = `docs/images/targets/${dong}_heatmap.png`;

    if (fs.existsSync(linePath)) {
        slide.addImage({ path: linePath, x: 0.2, y: 1.0, w: 4.6, h: 3.5 });
    }
    if (fs.existsSync(heatPath)) {
        slide.addImage({ path: heatPath, x: 5.2, y: 1.0, w: 4.6, h: 3.5 });
    }

    slide.addText("왼쪽: 시간대별 총 인구 흐름 | 오른쪽: 연령대별-시간대별 밀집도 히트맵", {
        x: 0.5, y: 4.8, w: 9, fontSize: 12, align: 'center'
    });
});

const outputPath = 'docs/서울_생활인구_EDA_리포트.pptx';
pres.writeFile({ fileName: outputPath }).then(fileName => {
    console.log(`PPTX 생성 완료: ${fileName}`);
}).catch(err => {
    console.error("Error saving PPTX:", err);
});
