/**
 * Formatting and parsing utilities for RAG responses
 */

/**
 * Format response for better display with HTML markup
 * Handles lists, code blocks, bold, italics, etc.
 */
export const formatResponse = (text) => {
  if (!text) return '';

  let html = text;

  // Convert markdown-style bold (**text** or __text__)
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

  // Convert markdown-style italics (*text* or _text_)
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.*?)_/g, '<em>$1</em>');

  // Convert inline code (`code`)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Convert code blocks (```code```)
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

  // Convert numbered lists
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Wrap consecutive list items in <ol>
  html = html.replace(/(<li>.*?<\/li>)/s, (match) => {
    if (!match.includes('<ol>')) {
      return '<ol>' + match.replace(/(<li>.*?<\/li>)/gs, '$1') + '</ol>';
    }
    return match;
  });

  // Convert unordered lists (- or * at start of line)
  html = html.replace(/^[*-]\s+(.+)$/gm, '<li>$1</li>');

  // Wrap consecutive list items in <ul>
  html = html.replace(/(<li>.*?<\/li>)/s, (match) => {
    if (!match.includes('<ul>') && !match.includes('<ol>')) {
      return '<ul>' + match.replace(/(<li>.*?<\/li>)/gs, '$1') + '</ul>';
    }
    return match;
  });

  // Convert headers (# Header)
  html = html.replace(/^#+\s+(.+)$/gm, (match, header) => {
    const level = match.match(/^#+/)[0].length;
    return `<h${Math.min(level, 3)}>${header}</h${Math.min(level, 3)}>`;
  });

  // Convert line breaks to paragraphs
  const paragraphs = html.split(/\n\n+/).map(para => {
    if (!para.match(/<(h|ul|ol|pre|blockquote|code)/)) {
      return `<p>${para.replace(/\n/g, '<br>')}</p>`;
    }
    return para;
  });

  html = paragraphs.join('');

  // Convert blockquotes (> quote)
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>');

  return html;
};

/**
 * Parse markdown in text
 */
export const parseMarkdown = (text) => {
  if (!text) return text;

  // Check if text contains markdown
  const markdownPatterns = [
    /\*\*(.*?)\*\*/g,      // bold
    /__(.*?)__/g,          // bold
    /\*(.*?)\*/g,          // italic
    /_(.*?)_/g,            // italic
    /`(.*?)`/g,            // code
    /```[\s\S]*?```/g,     // code block
    /^#+\s+/gm,            // headers
    /^[*-]\s+/gm,          // lists
    /^\d+\.\s+/gm,         // numbered lists
    /^>\s+/gm,             // blockquotes
  ];

  return markdownPatterns.some(pattern => pattern.test(text));
};

/**
 * Extract code blocks from text
 */
export const extractCodeBlocks = (text) => {
  const codeBlockPattern = /```([\s\S]*?)```/g;
  const matches = [];
  let match;

  while ((match = codeBlockPattern.exec(text)) !== null) {
    matches.push({
      code: match[1].trim(),
      start: match.index,
      end: match.index + match[0].length,
    });
  }

  return matches;
};

/**
 * Highlight code syntax (basic)
 */
export const highlightCode = (code, language = 'plain') => {
  let highlighted = code;

  // Basic Python highlighting
  if (language.includes('python')) {
    const keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return', 'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'pass', 'break', 'continue', 'lambda', 'yield'];
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`);
    });
  }

  // Basic JavaScript highlighting
  if (language.includes('javascript') || language.includes('js')) {
    const keywords = ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'import', 'export', 'async', 'await', 'try', 'catch', 'class'];
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`);
    });
  }

  return highlighted;
};

/**
 * Strip HTML tags from text
 */
export const stripHtml = (html) => {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
};

/**
 * Calculate confidence score from text
 */
export const calculateConfidence = (answer, documentCount) => {
  if (!answer || answer.length === 0) return 'low';
  if (documentCount >= 5) return 'high';
  if (documentCount >= 3) return 'medium';
  return 'low';
};

/**
 * Format answer length for display
 */
export const getAnswerLength = (answer) => {
  if (!answer) return 'very short';
  const length = answer.split(' ').length;
  if (length < 20) return 'very short';
  if (length < 50) return 'short';
  if (length < 150) return 'medium';
  if (length < 300) return 'long';
  return 'very long';
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 200) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Format timestamp for display
 */
export const formatTimestamp = (date) => {
  if (!date) return '';
  if (typeof date === 'string') date = new Date(date);
  
  const now = new Date();
  const diff = now - date;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  
  return date.toLocaleDateString();
};

/**
 * Extract sections from answer (numbered or bullet points)
 */
export const extractSections = (text) => {
  const sections = [];
  const lines = text.split('\n').filter(line => line.trim());

  let currentSection = null;
  lines.forEach(line => {
    // Check if line is a section header
    if (line.match(/^#{1,3}\s+/)) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        title: line.replace(/^#+\s+/, '').trim(),
        content: [],
      };
    } else if (currentSection && line.trim()) {
      currentSection.content.push(line);
    }
  });

  if (currentSection) sections.push(currentSection);
  return sections;
};

/**
 * Format response with emoji indicators
 */
export const formatWithEmoji = (text) => {
  let formatted = text;

  // Add emoji to common patterns
  const patterns = [
    [/^(Note|Important|Warning):/gm, '⚠️ $1:'],
    [/^(Tips?|Tip):/gm, '💡 $1:'],
    [/^(Example|Example):/gm, '📝 $1:'],
    [/^(Result|Output):/gm, '📊 $1:'],
    [/^(Error|Problem):/gm, '❌ $1:'],
    [/^(Success|Correct):/gm, '✓ $1:'],
  ];

  patterns.forEach(([pattern, replacement]) => {
    formatted = formatted.replace(pattern, replacement);
  });

  return formatted;
};

/**
 * Convert answer to exportable formats
 */
export const exportAnswer = (question, answer, format = 'markdown') => {
  const timestamp = new Date().toISOString();

  if (format === 'markdown') {
    return `# Q&A Export\n\n**Date:** ${timestamp}\n\n## Question\n${question}\n\n## Answer\n${answer}`;
  }

  if (format === 'json') {
    return JSON.stringify({
      timestamp,
      question,
      answer,
      exported: true,
    }, null, 2);
  }

  if (format === 'text') {
    return `Q: ${question}\n\nA: ${answer}\n\n---\nExported: ${timestamp}`;
  }

  return answer;
};

export default {
  formatResponse,
  parseMarkdown,
  extractCodeBlocks,
  highlightCode,
  stripHtml,
  calculateConfidence,
  getAnswerLength,
  truncate,
  formatTimestamp,
  extractSections,
  formatWithEmoji,
  exportAnswer,
};
