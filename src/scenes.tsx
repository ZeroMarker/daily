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

export const Intro: React.FC<{count: number; date: string}> = ({count, date}) => {
  const id = 'intro';
  const e1 = useEntrance(id, 0.1, 0.8);
  const e2 = useEntrance(id, 0.6, 0.8);
  return (
    <SceneShell id={id}>
      <AbsoluteFill
        style={{
          padding: '160px 84px',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          gap: 30,
        }}
      >
        <div
          style={{
            ...font,
            opacity: e1.opacity,
            transform: `translateY(${e1.y}px)`,
            display: 'flex',
            alignItems: 'center',
            gap: 18,
            color: C.accent,
            fontSize: 30,
            fontWeight: 800,
            letterSpacing: 8,
          }}
        >
          <span style={{width: 14, height: 14, borderRadius: '50%', background: C.accent}} /> AI 新闻日报
        </div>
        <div
          style={{
            ...font,
            opacity: e2.opacity,
            transform: `translateY(${e2.y}px)`,
            color: C.text,
            fontSize: 140,
            fontWeight: 900,
            letterSpacing: -4,
            lineHeight: 1,
          }}
        >
          {date}
        </div>
        <div style={{...font, opacity: e2.opacity, color: C.muted, fontSize: 34, fontWeight: 600}}>
          今日 {count} 条热点 · 每天 8 点更新
        </div>
        <div
          style={{
            opacity: e2.opacity,
            width: '100%',
            maxWidth: 760,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${C.accent}, transparent)`,
          }}
        />
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
  const titleSize = item.title.length > 12 ? 54 : 66;
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
            热
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
            {item.title}
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
              本期看点
            </div>
            <div style={{...font, color: C.text, fontSize: 34, fontWeight: 700, lineHeight: 1.3}}>
              {item.screenText}
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
          关注 · 每天与你 AI 读新闻
        </div>
        <div style={{...font, opacity: e.opacity, color: C.muted, fontSize: 24, fontWeight: 500}}>
          内容人工精选 · AI 配音
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
