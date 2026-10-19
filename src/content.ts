import data from '../public/voiceover/script.json';

export type ItemKind = 'intro' | 'news' | 'outro';

export interface NewsItem {
  id: string;
  kind: ItemKind;
  /** 屏幕大字标题 */
  title: string;
  /** 旁白段文本（与 narration.zh.txt 分段一一对应） */
  text: string;
  /** 画面关键点/数字 */
  screenText: string;
  /** 画面说明正文（区别于旁白 text，结构化的屏幕说明） */
  summary?: string;
  /** 新闻来源（news 类型才有） */
  source?: string;
  sourceUrl?: string;
  articleTitle?: string;
  publishedAt?: string;
  /** 开场总览：所有头条短标题（intro 才有） */
  headlines?: string[];
  /** 报道同一事件的媒体 */
  outlets?: string[];
  /** 来源分类（科技/财经/国际…） */
  category?: string;
}

interface ScriptManifest {
  date: string;
  items: NewsItem[];
}

export const DATE: string = (data as ScriptManifest).date;
export const ITEMS: NewsItem[] = (data as ScriptManifest).items;
