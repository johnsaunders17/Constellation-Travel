export async function fetchLatestResults(base = '') {
  const url = `${base}../results/latest.json`.replace(/\/+/, '/');
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}
