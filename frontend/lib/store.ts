import type { ChatSession } from "../types";

const KEY = "lexchain_sessions_v2";
const CUR = "lexchain_current_session_v2";
const MAX_SESSIONS = 30;

// الرد الخام (raw) بيتخزن للرد الأخير بس في كل جلسة، عشان حد localStorage (~5MB)
function slim(s: ChatSession): ChatSession {
  const last = s.messages.map((m) => m.role).lastIndexOf("ai");
  return {
    ...s,
    messages: s.messages.map((m, i) => (m.role === "ai" && i !== last ? { ...m, raw: undefined } : m)),
  };
}

export function loadSessions(): ChatSession[] {
  try {
    // تنظيف مفاتيح النسخة القديمة (كانت بتخزن العقد نفسها)
    localStorage.removeItem("lexchain_sessions");
    localStorage.removeItem("lexchain_current_session");
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
  } catch {
    return [];
  }
}

export function saveSessions(sessions: ChatSession[]) {
  let list = sessions.slice(0, MAX_SESSIONS).map(slim);
  while (list.length) {
    try {
      localStorage.setItem(KEY, JSON.stringify(list));
      return;
    } catch {
      list = list.slice(0, -1); // الحد اتعدّى: نشيل الأقدم
    }
  }
}

export const getCurrentId = () => localStorage.getItem(CUR);

export function setCurrentId(id: string | null) {
  if (id) localStorage.setItem(CUR, id);
  else localStorage.removeItem(CUR);
}

export const newSessionId = () => `session-${Date.now()}`;

export function upsertSession(list: ChatSession[], s: ChatSession): ChatSession[] {
  const old = list.find((x) => x.id === s.id);
  if (!old) return [s, ...list];
  return list.map((x) => (x.id === s.id ? { ...s, title: old.title } : x)); // العنوان يفضل أول سؤال
}
