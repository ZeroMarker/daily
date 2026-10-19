import React from 'react';
import {AbsoluteFill} from 'remotion';
import {notoSansSC} from './fonts';
import type {NewsItem} from './content';
import {useEntrance, useSceneOpacity, useSceneProgress} from './timing';

export const C = {
  bg: '#0b0e12',
  panel: 'rgba(255,255,255,.05)',
  text: '#f5f6f7',
  muted: '#8a929c',
  accent: '#ff5a3c',
  accent2: '#4aa3ff',
  line: 'rgba(255,255,255,.09)',
};

const font: React.CSSProperties = {
  fontFamily: `${notoSansSC.fontFamily}, 'Noto Sans SC', sans-serif`,
};

export const Backdrop: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        'radial-gradient(120% 80% at 70% -10%, rgba(74,163,255,.14), transparent 60%), radial-gradient(120% 80% at 10% 110%, rgba(255,90,60,.12), transparent 60%)',
    }}
  />
);

const SceneShell: React.FC<{id: string; children: React.ReactNode}> = ({id, children}) => {
  const opacity = useSceneOpacity(id);
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

const ProgressBar: React.FC<{id: string}> = ({id}) => {
  const p = useSceneProgress(id);
  return (
    <div style={{height: 8, borderRadius: 99, background: 'rgba(255,255,255,.08)', overflow: 'hidden'}}>
      <div
        style={{
          height: '100%',
          width: `${p * 100}%`,
          background: `linear-gradient(90deg, ${C.accent2}, ${C.accent})`,
        }}
      />
    </div>
  );
};

export const Intro: React.FC<{headlines: string[]; date: string}> = ({headlines, date}) => {
  const id = 'intro';
  const e1 = useEntrance(id, 0.05, 0.6);
  const progress = useSceneProgress(id);
  return (
    <SceneShell id={id}>
      <AbsoluteFill style={{padding: '150px 80px 140px', flexDirection: 'column', gap: 44}}>
        <div style={{opacity: e1.opacity, transform: `translateY(${e1.y}px)`}}>
          <div style={{...font, color: C.accent, fontSize: 34, fontWeight: 900, letterSpacing: 10}}>每日头条</div>
          <div style={{...font, color: C.text, fontSize: 96, fontWeight: 900, letterSpacing: -3, lineHeight: 1.1}}>
            {date}
          </div>
          <div style={{...font, color: C.muted, fontSize: 30, fontWeight: 600, marginTop: 8}}>北京时间 · 今日 {headlines.length} 条</div>
        </div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 22, flex: 1, justifyContent: 'center'}}>
          {headlines.map((headline, index) => {
            const delay = 0.15 + (index / Math.max(1, headlines.length)) * 0.55;
            const shown = Math.max(0, Math.min(1, (progress - delay) / 0.12));
            return (
              <div
                key={headline}
                style={{
                  opacity: shown,
                  transform: `translateX(${(1 - shown) * 40}px)`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 24,
                  background: C.panel,
                  border: `1px solid ${C.line}`,
                  borderRadius: 24,
                  padding: '26px 30px',
                }}
              >
                <div style={{...font, color: C.accent, fontSize: 44, fontWeight: 900, minWidth: 40}}>{index + 1}</div>
                <div style={{...font, color: C.text, fontSize: 38, fontWeight: 700, lineHeight: 1.3}}>{headline}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};

export const NewsCard: React.FC<{item: NewsItem}> = ({item}) => {
  const id = item.id;
  const header = useEntrance(id, 0.12, 0.7);
  const title = useEntrance(id, 0.3, 0.75);
  const summary = useEntrance(id, 0.6, 0.7);
  const highlight = useEntrance(id, 0.9, 0.7);
  const heading = item.articleTitle ?? item.title;
  const titleSize = heading.length > 24 ? 52 : heading.length > 12 ? 60 : 68;
  return (
    <SceneShell id={id}>
      <AbsoluteFill style={{padding: '90px 82px 110px', flexDirection: 'column'}}>
        {/* 来源标签 */}
        <div style={{opacity: header.opacity, transform: `translateY(${header.y}px)`, display: 'flex', alignItems: 'center', gap: 18}}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: C.accent,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontWeight: 900,
              fontSize: 26,
            }}
          >
            {item.id.replace('news-', '')}
          </div>
          <div>
            <div style={{...font, color: C.accent, fontWeight: 900, fontSize: 30, letterSpacing: 1}}>
              {item.source}
            </div>
            <div style={{...font, color: C.muted, fontSize: 23, fontWeight: 600}}>{item.category}</div>
          </div>
        </div>

        {/* 标题 + 说明 + 看点：竖向居中 */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 36}}>
          <div
            style={{
              ...font,
              opacity: title.opacity,
              transform: `translateY(${title.y}px) scale(${title.scale})`,
              transformOrigin: 'left center',
              color: C.text,
              fontSize: titleSize,
              fontWeight: 900,
              lineHeight: 1.22,
              letterSpacing: -2,
            }}
          >
            {heading}
          </div>

          <div
            style={{
              opacity: summary.opacity,
              transform: `translateY(${summary.y}px)`,
              background: C.panel,
              border: `1px solid ${C.line}`,
              borderRadius: 26,
              padding: '28px 32px',
            }}
          >
            <div style={{...font, color: C.accent2, fontSize: 23, fontWeight: 700, marginBottom: 12, letterSpacing: 2}}>
              内容
            </div>
            <div style={{...font, color: C.text, fontSize: 34, fontWeight: 500, lineHeight: 1.46}}>
              {item.summary}
            </div>
          </div>

          <div
            style={{
              opacity: highlight.opacity,
              transform: `translateY(${highlight.y}px)`,
              display: 'flex',
              alignItems: 'center',
              gap: 18,
              background: 'rgba(255,90,60,.08)',
              border: '1px solid rgba(255,90,60,.28)',
              borderRadius: 24,
              padding: '26px 30px',
            }}
          >
            <div style={{...font, color: C.accent, fontSize: 24, fontWeight: 900, letterSpacing: 2, whiteSpace: 'nowrap'}}>
              报道来源
            </div>
            <div style={{...font, color: C.text, fontSize: 34, fontWeight: 700, lineHeight: 1.3}}>
              {(item.outlets ?? [item.source]).join(' · ')}
            </div>
          </div>
        </div>

        <ProgressBar id={id} />
      </AbsoluteFill>
    </SceneShell>
  );
};

export const Outro: React.FC = () => {
  const id = 'outro';
  const e = useEntrance(id, 0.2, 0.8);
  return (
    <SceneShell id={id}>
      <AbsoluteFill
        style={{
          padding: '180px 84px',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          gap: 28,
        }}
      >
        <div
          style={{
            ...font,
            opacity: e.opacity,
            transform: `translateY(${e.y}px)`,
            color: C.text,
            fontSize: 112,
            fontWeight: 900,
            letterSpacing: -4,
          }}
        >
          明天见
        </div>
        <div style={{...font, opacity: e.opacity, color: C.accent, fontSize: 38, fontWeight: 800, letterSpacing: 2}}>
          每日头条 · 原文链接见文字版
        </div>
        <div style={{...font, opacity: e.opacity, color: C.muted, fontSize: 24, fontWeight: 500}}>
          多源交叉印证 · 自动摘要 · AI 配音
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
