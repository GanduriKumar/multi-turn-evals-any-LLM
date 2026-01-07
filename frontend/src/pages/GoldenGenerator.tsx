import React, { useMemo, useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import { Select, Checkbox } from '../components/Form'

 

type Domain = 'commerce' | 'banking'

type ConversationTurn = { role: 'user' | 'assistant', text: string }

type DatasetDoc = {
  dataset_id: string
  version: string
  metadata: { domain: Domain, difficulty: 'easy'|'medium'|'hard', tags?: string[] }
  conversations: { conversation_id: string, turns: ConversationTurn[] }[]
}

type GoldenDoc = {
  dataset_id: string
  version: string
  entries: { conversation_id: string, turns: { turn_index: number, expected: { variants: string[] } }[], final_outcome: { decision: 'ALLOW'|'DENY'|'PARTIAL', refund_amount?: number, reason_code?: string, next_action?: string, policy_flags?: string[] } }[]
}

function genId(prefix: string) {
  const n = Math.floor(Math.random()*1e6).toString(36)
  return `${prefix}-${n}`
}

function buildConversation(domain: Domain, difficulty: 'easy'|'medium'|'hard', outcome: 'ALLOW'|'DENY'|'PARTIAL'): {dataset: DatasetDoc, golden: GoldenDoc} {
  const dataset_id = genId(`${domain}-${difficulty}-${outcome}`)
  const version = '1.0.0'
  const convoId = genId('conv')

  const userProblem = domain === 'commerce'
    ? 'My order arrived damaged. I want a refund.'
    : 'I noticed a suspicious transaction. Can you help?'

  const assistantProbe = domain === 'commerce'
    ? 'I am sorry to hear that. Could you share your order ID and item details?'
    : 'I can help. Could you share the transaction ID and amount?'

  const userDetails = domain === 'commerce'
    ? 'Order #A123, item: headphones, price $79.'
    : 'Transaction T-9876 for $250 yesterday.'

  const assistantPolicy = domain === 'commerce'
    ? 'Based on the policy, we can process a refund if damage is confirmed.'
    : 'According to policy, we can freeze the card and start a dispute.'

  const assistantResolution = outcome === 'ALLOW'
    ? (domain === 'commerce' ? 'I have approved a full refund of $79.' : 'I have blocked your card and started a dispute; you will be reimbursed $250 if validated.')
    : outcome === 'PARTIAL'
      ? (domain === 'commerce' ? 'I can offer a partial refund of $40.' : 'We can issue a temporary credit of $100 pending investigation.')
      : (domain === 'commerce' ? 'We cannot refund without proof of damage. Please provide photos.' : 'We cannot credit without verification. Please submit a dispute form.')

  const dataset: DatasetDoc = {
    dataset_id,
    version,
    metadata: { domain, difficulty, tags: ['template'] },
    conversations: [
      {
        conversation_id: convoId,
        turns: [
          { role: 'user', text: userProblem },
          { role: 'assistant', text: assistantProbe },
          { role: 'user', text: userDetails },
          { role: 'assistant', text: assistantPolicy },
          { role: 'user', text: 'Thanks, what can you do for me now?' },
          { role: 'assistant', text: assistantResolution },
        ],
      }
    ]
  }

  const golden: GoldenDoc = {
    dataset_id,
    version,
    entries: [
      {
        conversation_id: convoId,
        turns: [
          { turn_index: 1, expected: { variants: [assistantProbe] } },
          { turn_index: 3, expected: { variants: [assistantPolicy] } },
          { turn_index: 5, expected: { variants: [assistantResolution] } },
        ],
        final_outcome: {
          decision: outcome,
          refund_amount: domain === 'commerce' ? (outcome === 'ALLOW' ? 79 : outcome === 'PARTIAL' ? 40 : 0) : undefined,
          next_action: domain === 'banking' ? (outcome === 'ALLOW' ? 'dispute' : 'verify') : undefined,
          policy_flags: outcome === 'DENY' ? ['NEEDS_EVIDENCE'] : [],
        }
      }
    ]
  }

  return { dataset, golden }
}

export default function GoldenGeneratorPage() {
  const [domain, setDomain] = useState<Domain>('commerce')
  const [difficulty, setDifficulty] = useState<'easy'|'medium'|'hard'>('easy')
  const [outcome, setOutcome] = useState<'ALLOW'|'DENY'|'PARTIAL'>('ALLOW')
  const [bundle, setBundle] = useState<{dataset: any, golden: any} | null>(null)
  const [bundles, setBundles] = useState<Array<{dataset: any, golden: any}>>([])
  const [combined, setCombined] = useState<{dataset:any, golden:any} | null>(null)
  const [overwriteSave, setOverwriteSave] = useState(false)
  const [savingMsg, setSavingMsg] = useState<string | null>(null)
  const [savingErr, setSavingErr] = useState<string | null>(null)

  const generate = () => {
    const b = buildConversation(domain, difficulty, outcome)
    setBundle(b)
    setBundles([])
    setCombined(null)
  }

  const generateAll = () => {
    const diffs: Array<'easy'|'medium'|'hard'> = ['easy', 'medium', 'hard']
    const outs: Array<'ALLOW'|'DENY'|'PARTIAL'> = ['ALLOW', 'DENY', 'PARTIAL']
    const all: Array<{dataset:any, golden:any}> = []
    for (const d of diffs) {
      for (const o of outs) {
        all.push(buildConversation(domain, d, o))
      }
    }
    setBundles(all)
    setBundle(null)
    setCombined(null)
  }

  const generateCombined = () => {
    const diffs: Array<'easy'|'medium'|'hard'> = ['easy', 'medium', 'hard']
    const outs: Array<'ALLOW'|'DENY'|'PARTIAL'> = ['ALLOW', 'DENY', 'PARTIAL']
    const all: Array<{dataset:any, golden:any}> = []
    for (const d of diffs) {
      for (const o of outs) {
        all.push(buildConversation(domain, d, o))
      }
    }
    const combinedId = `${domain}-combined-coverage`
    const ds = {
      dataset_id: combinedId,
      version: '1.0.0',
      metadata: { domain, difficulty: 'mixed', tags: ['coverage','combined'] },
      conversations: all.flatMap(b => b.dataset.conversations)
    }
    const gd = {
      dataset_id: combinedId,
      version: '1.0.0',
      entries: all.flatMap(b => b.golden.entries)
    }
    setCombined({ dataset: ds, golden: gd })
    setBundle(null)
    setBundles([])
  }

  const download = (name: 'dataset'|'golden') => {
    if (!bundle) return
    const blob = new Blob([JSON.stringify(bundle[name], null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${bundle[name].dataset_id}.${name}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadFrom = (name: 'dataset'|'golden', item: {dataset:any, golden:any}) => {
    const blob = new Blob([JSON.stringify(item[name], null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${item[name].dataset_id}.${name}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const savePair = async (pair: {dataset:any, golden:any}) => {
    setSavingMsg(null); setSavingErr(null)
    try {
      const r = await fetch('/datasets/save', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ dataset: pair.dataset, golden: pair.golden, overwrite: overwriteSave, bump_version: false })
      })
      const js = await r.json()
      if (!r.ok) throw new Error(js?.detail ? (typeof js.detail === 'string' ? js.detail : JSON.stringify(js.detail)) : 'Save failed')
      setSavingMsg(`Saved ${js.dataset_id} v${js.version || pair.dataset.version}`)
    } catch (e:any) {
      setSavingErr(e.message || 'Save failed')
    }
  }

  const saveAll = async () => {
    setSavingMsg(null); setSavingErr(null)
    try {
      let ok = 0
      for (const p of bundles) {
        const r = await fetch('/datasets/save', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ dataset: p.dataset, golden: p.golden, overwrite: overwriteSave, bump_version: false })
        })
        if (!r.ok) {
          const js = await r.json().catch(() => ({}))
          throw new Error(js?.detail ? (typeof js.detail === 'string' ? js.detail : JSON.stringify(js.detail)) : `Save failed for ${p.dataset?.dataset_id}`)
        }
        ok += 1
      }
      setSavingMsg(`Saved ${ok} datasets to server`)
    } catch (e:any) {
      setSavingErr(e.message || 'Save failed')
    }
  }

  return (
    <div className="grid gap-4">
      <Card title="Golden Generator">
        <div className="grid sm:grid-cols-3 gap-4 text-sm">
          <label className="flex items-center gap-2"><span className="w-28">Domain</span>
            <Select className="grow" value={domain} onChange={e => setDomain(e.target.value as Domain)}>
              <option value="commerce">Commerce</option>
              <option value="banking">Banking</option>
            </Select>
          </label>
          <label className="flex items-center gap-2"><span className="w-28">Difficulty</span>
            <Select className="grow" value={difficulty} onChange={e => setDifficulty(e.target.value as any)}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </Select>
          </label>
          <label className="flex items-center gap-2"><span className="w-28">Outcome</span>
            <Select className="grow" value={outcome} onChange={e => setOutcome(e.target.value as any)}>
              <option value="ALLOW">ALLOW</option>
              <option value="DENY">DENY</option>
              <option value="PARTIAL">PARTIAL</option>
            </Select>
          </label>
        </div>
        <div className="mt-4 flex flex-wrap gap-2 items-center">
          <Button variant="primary" onClick={generate}>Generate</Button>
          <Button variant="primary" onClick={generateAll}>Generate 100% coverage</Button>
          <Button variant="warning" onClick={generateCombined}>Generate combined (100%)</Button>
          <label className="inline-flex items-center gap-2 ml-2 text-sm"><Checkbox checked={overwriteSave} onChange={e => setOverwriteSave((e.target as HTMLInputElement).checked)} /> Overwrite on save</label>
          {savingMsg && <span className="text-sm text-success">{savingMsg}</span>}
          {savingErr && <span className="text-sm text-danger">{savingErr}</span>}
        </div>
      </Card>

      {bundle && (
        <Card title="Preview & Download">
          <div className="flex flex-wrap gap-2 mb-2">
            <Button variant="secondary" onClick={() => download('dataset')}>Download dataset.json</Button>
            <Button variant="secondary" onClick={() => download('golden')}>Download golden.json</Button>
            <Button variant="success" onClick={() => savePair(bundle)}>Save to server</Button>
          </div>
          <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-80">{JSON.stringify(bundle, null, 2)}</pre>
        </Card>
      )}

      {combined && (
        <Card title="Combined (100%) Preview & Download">
          <div className="flex flex-wrap gap-2 mb-2">
            <Button variant="secondary" onClick={() => downloadFrom('dataset', combined)}>Download combined dataset.json</Button>
            <Button variant="secondary" onClick={() => downloadFrom('golden', combined)}>Download combined golden.json</Button>
            <Button variant="success" onClick={() => savePair(combined)}>Save combined to server</Button>
          </div>
          <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-80">{JSON.stringify(combined, null, 2)}</pre>
        </Card>
      )}

      {bundles.length > 0 && (
        <Card title={`Coverage Preview (${bundles.length})`}>
          <div className="text-sm text-gray-700 mb-2">Domain: {domain} — Difficulties: easy, medium, hard — Outcomes: ALLOW, DENY, PARTIAL</div>
          <div className="mb-3">
            <Button variant="success" onClick={saveAll}>Save all to server</Button>
          </div>
          <div className="space-y-3">
            {bundles.map((b, idx) => (
              <div key={b.dataset.dataset_id || idx} className="rounded border border-gray-200 p-3">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className="font-mono text-xs">{b.dataset.dataset_id}</span>
                  <span className="text-xs text-gray-500">v{b.dataset.version}</span>
                  <div className="grow" />
                  <Button variant="secondary" onClick={() => downloadFrom('dataset', b)}>dataset.json</Button>
                  <Button variant="secondary" onClick={() => downloadFrom('golden', b)}>golden.json</Button>
                  <Button variant="success" onClick={() => savePair(b)}>save</Button>
                </div>
                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-48">{JSON.stringify(b, null, 2)}</pre>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
