import {useCurrentFrame, useVideoConfig} from 'remotion';
import durations from '../public/voiceover/segment-durations.json';
import {ITEMS} from './content';

export const FPS = 30;

const sceneIds = ITEMS.map((item) => item.id);

if (durations.length !== sceneIds.length) {
  throw new Error(
    '旁白段落数与场景数不一致：请先按顺序运行 npm run news 生成 script.json，再运行 npm run voiceover。',
  );
}

export const SCENES: {id: string; start: number; end: number}[] = [];
let cursor = 0;
for (let index = 0; index < sceneIds.length; index++) {
  const start = cursor;
  cursor += durations[index];
  SCENES.push({id: sceneIds[index], start, end: cursor});
}

export const AUDIO_END = cursor;
export const TOTAL_SECONDS = Math.ceil(AUDIO_END + 2.6);

export const sceneById = (id: string) => SCENES.find((scene) => scene.id === id)!;

export const useSceneProgress = (id: string) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scene = sceneById(id);
  return Math.max(0, Math.min(1, (frame / fps - scene.start) / (scene.end - scene.start)));
};

export const useSceneOpacity = (id: string) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const scene = sceneById(id);
  const fade = 0.38;
  if (time >= scene.start && time <= scene.end) return 1;
  if (time >= scene.start - fade && time < scene.start) return (time - scene.start + fade) / fade;
  if (time > scene.end && time <= scene.end + fade) return 1 - (time - scene.end) / fade;
  return 0;
};

export const useEntrance = (id: string, offset = 0, duration = 0.65) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scene = sceneById(id);
  const raw = (frame / fps - scene.start - offset) / duration;
  const p = Math.max(0, Math.min(1, raw));
  const eased = 1 - Math.pow(1 - p, 3);
  return {opacity: eased, y: (1 - eased) * 34, scale: 0.92 + eased * 0.08};
};
