/** The public reader contains teaching material, not research/verification logs. */
import path from 'node:path';

export const isReadingDocument = file =>
  /^(?:README|QUESTION_INDEX)\.md$/.test(file) ||
  /^(?:docs|examples)\/.+\.md$/.test(file) &&
  !/(?:^|\/)(?:SOURCES|TESTING|VALIDATION|LICENSE|NOTICE)(?:\.[^/]*)?\.md$/i.test(file);

export const isTeachingResource = file =>
  (/^(?:examples|tests)\//.test(file) &&
  /\.(?:py|java|go|mod|sql)$/.test(file) &&
  !/(?:check_carl_resources|validate_sources)/.test(file)) ||
  file === 'examples/requirements.txt' ||
  file === 'examples/public_interview_scenarios/evaluation_design_template.json';

// Fixed public implementation locations remain useful to explain project code.
// General article/video/author links are not part of the reading presentation.
export const isProjectCodeUrl = href =>
  /^https:\/\/github\.com\/(?:[^/]+\/){2}blob\/[a-f0-9]{40}\/(?!.*(?:README\.md|LICENSE|NOTICE)(?:#|$))[^?#]+(?:#[^?]*)?$/i.test(href);

export function readingMarkdown(source, file) {
  // This is a defensive publication boundary. Repository teaching Markdown is
  // cleaned too, but older research links must not reappear through raw source,
  // search text, a hidden reader page, or a resource download.
  let fence = null;
  let skipDepth = 0;
  const lines = [];
  const metadataHeading = /^(?:(?:[一二三四五六七八九十]+|\d+)[、.\s]+)?(?:参考(?:资料|文献|链接)?|资料来源|来源(?:与(?:复验|技术合同|权利边界|阅读边界))?|出处|代码随想录延伸阅读|延伸阅读|官方参考|两篇新来源|来源\s*[AB]：.*)$/;
  for (let line of source.split('\n')) {
    const marker = line.match(/^\s*(`{3,}|~{3,})/);
    if (marker) {
      if (!fence) fence = marker[1][0];
      else if (marker[1][0] === fence) fence = null;
      if (!skipDepth) lines.push(line);
      continue;
    }
    if (fence) { if (!skipDepth) lines.push(line); continue; }
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      if (skipDepth && heading[1].length <= skipDepth) skipDepth = 0;
      if (metadataHeading.test(heading[2].trim())) skipDepth = heading[1].length;
    }
    if (skipDepth) continue;
    // Explicit stable anchors must remain their own Markdown block even when
    // an editor removes surrounding blank lines next to a list or table.
    if (/^\s*<a\s+id=["'][\w-]+["']\s*>\s*<\/a>\s*$/.test(line)) {
      lines.push('',line,'');
      continue;
    }
    // Only standalone editorial labels are removed. Technical prose about
    // data/evidence provenance and validation remains ordinary teaching content.
    if (/^\s*(?:[-*]\s+)?(?:\*\*)?(?:主题来源|技术依据|资料来源|参考资料|原帖|原文标题|作者|核验日期|来源核查日期)(?:\*\*)?\s*[：:]/.test(line)) continue;
    if (/^\s*\*\*来源\*\*\s*[：:]?/.test(line)) continue;
    const cleanText = text => text.replace(/\[([^\]]+)\]\(([^\s)]+)(?:\s+"[^"]*")?\)/g, (whole, label, href) => {
      if (/^https?:/i.test(href)) return isProjectCodeUrl(href) ? whole : label;
      if (/^[a-z][\w+.-]*:/i.test(href)) return '';
      let local;
      try { local = decodeURIComponent(href.split(/[?#]/)[0]); } catch { return label; }
      if (!local) return whole;
      const target = path.posix.normalize(path.posix.join(path.posix.dirname(file), local));
      if ((target.endsWith('.md') && isReadingDocument(target)) || isTeachingResource(target)) return whole;
      return '';
    }).replace(/(?:https?:\/\/[^\s<>）)]+)(?=[\s）)]|$)/g, href => isProjectCodeUrl(href) ? href : '');
    // A URL inside inline code may be the actual request/endpoint being taught.
    // Protect it just as fenced code is protected above.
    line = line.split(/(`+[^`]*`+)/g).map(part => part.startsWith('`') ? part : cleanText(part)).join('');
    // Remove separator remnants after filtering a source-only navigation link.
    line = line.replace(/(?:\s*·\s*)+$/, '').replace(/^\s*·\s*/, '');
    if (/^\s*[。；，、·]*\s*$/.test(line)) line = '';
    lines.push(line);
  }
  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
}
