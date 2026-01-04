import { useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import PageHeader from '../components/layout/PageHeader'

export type DatasetInfo = {
  id: string;
  name: string;
  conversation: string;
  golden: string;
  conversation_version?: string | null;
  golden_version?: string | null;
  tags: string[];
  difficulty?: string | null;
};

async function fetchDatasets(): Promise<DatasetInfo[]> {
  const res = await fetch('/api/v1/datasets/?page=1&page_size=1000');
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load datasets: ${res.status} ${text}`);
  }
  const body = await res.json();
  const arr: any[] = Array.isArray(body)
    ? body
    : Array.isArray(body?.items)
    ? body.items
    : Array.isArray(body?.datasets)
    ? body.datasets
    : Array.isArray(body?.data)
    ? body.data
    : [];
  return arr.map((d) => ({
    id: String(d.id ?? d.name ?? ''),
    name: String(d.name ?? d.id ?? ''),
    conversation: String(d.conversation ?? ''),
    golden: String(d.golden ?? ''),
    conversation_version: d.conversation_version ?? null,
    golden_version: d.golden_version ?? null,
    tags: Array.isArray(d.tags) ? d.tags : [],
    difficulty: d.difficulty ?? null,
  }))
}

export default function DatasetsPage() {
  const [items, setItems] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [domain, setDomain] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [reloading, setReloading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDatasets();
      setItems(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function refresh() {
    setReloading(true);
    await load();
    setReloading(false);
  }

  const domains = useMemo(() => {
    const s = new Set<string>();
    items.forEach((d) => (d.tags || []).forEach((t) => s.add(t)));
    return [''].concat(Array.from(s).sort());
  }, [items]);
  const difficulties = useMemo(() => {
    const s = new Set<string>();
    items.forEach((d) => d.difficulty && s.add(d.difficulty));
    return [''].concat(Array.from(s).sort());
  }, [items]);

  const filtered = useMemo(() => {
    return items.filter((d) => {
      const domainOk = !domain || (d.tags || []).includes(domain);
      const diffOk = !difficulty || d.difficulty === difficulty;
      return domainOk && diffOk;
    });
  }, [items, domain, difficulty]);

  const toggle = (id: string) => setSelected((p) => ({ ...p, [id]: !p[id] }));
  const selectedIds = Object.entries(selected).filter(([_, v]) => v).map(([k]) => k);

  return (
    <div>
      <PageHeader title="Datasets" subtitle="Filter, select, and load datasets to start a run" />
      <Card className="mb-4">
        <CardContent>
          <div className="flex gap-4 items-end">
            <div>
              <label htmlFor="domain" className="block text-sm font-medium">Domain</label>
              <select id="domain" className="border border-slate-300 rounded p-2 focus:outline-none focus:ring-1 focus:ring-google-blue focus:border-google-blue bg-white" value={domain} onChange={(e) => setDomain(e.target.value)}>
                {domains.map((d) => (
                  <option key={d} value={d}>{d || 'All'}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="difficulty" className="block text-sm font-medium">Difficulty</label>
              <select id="difficulty" className="border border-slate-300 rounded p-2 focus:outline-none focus:ring-1 focus:ring-google-blue focus:border-google-blue bg-white" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                {difficulties.map((d) => (
                  <option key={d} value={d}>{d || 'All'}</option>
                ))}
              </select>
            </div>
            <div className="ml-auto flex gap-2">
              <Button onClick={refresh} disabled={reloading}>{reloading ? 'Refreshing…' : 'Refresh'}</Button>
              <Button onClick={() => setSelected(Object.fromEntries(filtered.map((d) => [d.id, true])))}>Select All (filtered)</Button>
              <Button onClick={() => setSelected({})}>Clear Selection</Button>
              <Button to={{ pathname: '/run-setup', search: selectedIds.length ? `?datasets=${selectedIds.join(',')}` : '' }} variant="primary">
                Load Selected ({selectedIds.length})
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading && <div>Loading…</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && filtered.length === 0 && (
        <div className="text-sm text-gray-600">No datasets found. Try Refresh or check your datasets folder.</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((d) => (
          <Card key={d.id} className="p-0">
            <CardHeader>
              <div className="flex items-start gap-3">
                <input type="checkbox" checked={!!selected[d.id]} onChange={() => toggle(d.id)} className="mt-1"/>
                <div className="flex-1">
                  <CardTitle className="text-slate-900">{d.name}</CardTitle>
                  <div className="text-xs text-gray-600">ID: {d.id}</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(d.tags || []).map((t) => (
                      <Badge key={t}>{t}</Badge>
                    ))}
                    {d.difficulty && (
                      <Badge tone="info">{d.difficulty}</Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-500">
                conv v{d.conversation_version || '-'} · golden v{d.golden_version || '-'}
              </div>
              <div className="mt-3 flex gap-2">
                <Button onClick={() => toggle(d.id)} variant={selected[d.id] ? 'secondary' : 'outline'}>
                  {selected[d.id] ? 'Deselect' : 'Select'}
                </Button>
                <Button to={{ pathname: '/run-setup', search: `?datasets=${encodeURIComponent(d.id)}` }} variant="primary">
                  Load Dataset
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
