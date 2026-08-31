import React from 'react';
import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {notoSansSC} from './fonts';
import {DATE, ITEMS} from './content';
import {AUDIO_END} from './timing';
import {Backdrop, C, Intro, NewsCard, Outro} from './scenes';

const font: React.CSSProperties = {
  fontFamily: `${notoSansSC.fontFamily}, 'Noto Sans SC', sans-serif`,
};

export const NewsDaily: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const newsItems = ITEMS.filter((item) => item.kind === 'news');
  const dateLabel = DATE.replace(/^\d{4}-0?(\d+)-0?(\d+)$/, '$1月$2日');
  const fade = interpolate(frame / fps, [AUDIO_END + 0.5, AUDIO_END + 2.4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Backdrop />
      <Intro count={newsItems.length} date={dateLabel} />
      {newsItems.map((item) => (
        <NewsCard key={item.id} item={item} />
      ))}
      <Outro />
      <Audio src={staticFile('voiceover/narration.zh.mp3')} />
      <AbsoluteFill style={{background: '#050609', opacity: fade}} />
      <div
        style={{
          position: 'absolute',
          left: 60,
          bottom: 48,
          ...font,
          color: 'rgba(138,146,156,.5)',
          fontSize: 20,
          fontWeight: 600,
          letterSpacing: 2,
        }}
      >
        AI 新闻日报 · {DATE}
      </div>
    </AbsoluteFill>
  );
};
