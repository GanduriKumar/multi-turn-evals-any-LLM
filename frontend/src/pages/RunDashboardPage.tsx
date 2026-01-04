import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import Button from '../components/ui/Button'

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <svg key={i} className={`w-4 h-4 ${i <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  )
}

function GradientProgressBar({ value }: { value: number }) {
  return (
    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
      <div className="h-full bg-gradient-to-r from-blue-400 to-yellow-300" style={{ width: `${value}%` }} />
    </div>
  )
}

export default function RunDashboardPage() {
  const { runId = '112' } = useParams();

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6 bg-gray-50 min-h-screen font-sans text-slate-800">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Multi-Turn LLM Evaluation</h1>
          <p className="text-slate-500 mt-1">Evaluated #{runId}</p>
        </div>
        <Button variant="outline" className="flex items-center gap-2 bg-white text-slate-700 border-slate-300">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
          Download Report
        </Button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left Column */}
        <div className="col-span-12 lg:col-span-7 space-y-6">
          
          {/* Define Test Scenarios */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
                <CardTitle className="text-lg">Define Test Scenarios</CardTitle>
              </div>
              <Button variant="outline" size="sm" className="text-xs">Edit Dataset</Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-50 p-3 rounded-md border border-slate-100">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="font-medium text-slate-700">Dataset: technical_support</div>
                    <div className="text-xs text-slate-500">Conversations: 25</div>
                  </div>
                  <Button variant="outline" size="sm" className="text-xs bg-white h-7">Edit Dataset ▾</Button>
                </div>
                
                <div className="space-y-3 mt-3">
                  <div className="bg-white p-3 rounded border border-slate-100 shadow-sm">
                    <div className="text-sm text-blue-600 font-medium mb-1">USER: How do I reset my account password?</div>
                    <div className="text-sm text-slate-600 flex items-center gap-1">
                      <span className="font-medium text-slate-700">ASSISTANT:</span> I can help with that! Please go the login page... 
                      <span className="text-blue-500 text-xs cursor-pointer hover:underline">▾ Show full dialogue</span>
                    </div>
                  </div>
                  
                  <div className="bg-white p-3 rounded border border-slate-100 shadow-sm opacity-75">
                    <div className="text-sm text-blue-600 font-medium mb-1">ASSISTANT: Are you able to assist me with my computer's slow performance?</div>
                    <div className="text-sm text-slate-600">
                      <span className="font-medium text-slate-700">ASSISTANT:</span> Certainly! Can you provide more details on the issue you're experiencing?
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* LLM Configuration */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <div className="h-4 w-4 rounded-full bg-green-500 flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                </div>
                <CardTitle className="text-lg">LLM Configuration</CardTitle>
              </div>
              <Button variant="outline" size="sm" className="text-xs">Edit LLM ▸</Button>
            </CardHeader>
            <CardContent>
              <div className="bg-slate-50 p-4 rounded-md border border-slate-100 flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-800 text-lg">Gemini 1.5 Pro</div>
                  <div className="text-sm text-slate-500">Gemini Providers</div>
                </div>
                <div className="text-right text-sm text-slate-600 space-y-1">
                  <div className="flex justify-end gap-4">
                    <span>Test turns</span>
                    <span className="font-medium">Max ▾</span>
                  </div>
                  <div className="flex justify-end gap-4">
                    <span>Temp</span>
                    <span className="font-medium">0.7 ▾</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Turn Control */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
                <CardTitle className="text-lg">Turn Control</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-50 p-4 rounded-md border border-slate-100 space-y-4">
                <div className="text-sm font-medium text-slate-500">Turn 1 of 5</div>
                
                <div className="bg-white p-3 rounded border border-slate-100 shadow-sm flex justify-between items-start">
                  <div className="text-sm">
                    <span className="text-blue-600 font-bold uppercase text-xs mr-2">USER</span>
                    How do I reset my account password?
                  </div>
                  <StarRating rating={4} />
                </div>

                <div className="bg-white p-3 rounded border border-slate-100 shadow-sm flex justify-between items-start">
                  <div className="text-sm">
                    <span className="text-indigo-600 font-bold text-xs mr-2">Gemini 1.5 Pro:</span>
                    I can help with that! Please go to the login page at the top of the site, click "Forgot Password?", and follow the prompts...
                  </div>
                  <StarRating rating={4} />
                </div>
              </div>
              
              <div>
                <Button variant="outline" size="sm" className="text-slate-600">← Previous Turn</Button>
              </div>
            </CardContent>
          </Card>

        </div>

        {/* Right Column */}
        <div className="col-span-12 lg:col-span-5 space-y-6">
          
          {/* Metrics Selection */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                <CardTitle className="text-lg">Metrics Selection</CardTitle>
              </div>
              <Button variant="outline" size="sm" className="text-xs">Edit Metrics</Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { name: 'Completeness', weight: '0.5', score: 4, color: 'bg-green-500' },
                { name: 'Relevance', weight: '0.5', score: 4, color: 'bg-green-500' },
                { name: 'Correctness', weight: '1.0', score: 4, color: 'bg-green-500' },
              ].map((m) => (
                <div key={m.name} className="bg-slate-50 p-3 rounded-md border border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded-full bg-green-500 flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                    </div>
                    <span className="font-medium text-sm text-slate-700">{m.name}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-500">{m.weight} Weight</span>
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className={`h-full ${m.color}`} style={{ width: '70%' }}></div>
                    </div>
                    <StarRating rating={m.score} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Run Control */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                <CardTitle className="text-lg">Run Control</CardTitle>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="text-xs h-7">Pause ▾</Button>
                <Button variant="danger" size="sm" className="text-xs h-7">Abort ▾</Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <div className="flex items-center gap-2 text-sm text-slate-700 mb-1">
                    <span className="bg-blue-100 text-blue-700 text-xs font-bold px-1.5 py-0.5 rounded">1</span>
                    Running Tests <span className="animate-spin text-slate-400">↻</span>
                  </div>
                  <GradientProgressBar value={85} />
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-slate-700 mb-1">
                    <span className="bg-blue-100 text-blue-700 text-xs font-bold px-1.5 py-0.5 rounded">2</span>
                    Scoring Responses:
                  </div>
                  <GradientProgressBar value={60} />
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-slate-700 mb-1">
                    <span className="bg-blue-100 text-blue-700 text-xs font-bold px-1.5 py-0.5 rounded">3</span>
                    Evaluating Metrics:
                  </div>
                  <GradientProgressBar value={40} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Turn Review */}
          <Card>
            <div className="border-b border-gray-200">
              <div className="flex">
                <button className="px-4 py-3 text-sm font-medium text-slate-800 border-b-2 border-slate-800 bg-slate-50">Turn Review</button>
                <button className="px-4 py-3 text-sm font-medium text-slate-500 hover:text-slate-700">Summary</button>
              </div>
            </div>
            <CardContent className="pt-4">
              <div className="text-sm font-medium text-slate-500 mb-3">Turn 1 of 5</div>
              
              <div className="flex gap-4 h-48">
                <div className="flex-1 space-y-3 overflow-y-auto pr-2">
                  <div className="bg-blue-50 p-2 rounded text-sm text-slate-700">
                    <span className="text-blue-600 font-bold text-xs block mb-1">USER:</span>
                    How do to the login page...
                  </div>
                  <div className="bg-white border border-slate-100 p-2 rounded text-sm text-slate-700">
                    <span className="text-indigo-600 font-bold text-xs block mb-1">Gemini 1.5 Pro</span>
                    (I can help with that! Please go to the <span className="text-green-600">login page.</span>) at the top of the site, click the <span className="text-red-500">"Forgot Password"</span>.
                  </div>
                </div>
                <div className="flex-1">
                  <textarea 
                    className="w-full h-full p-3 text-sm border border-slate-200 rounded resize-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Human Review Notes..."
                  ></textarea>
                </div>
              </div>

              <div className="flex justify-between mt-4 pt-4 border-t border-slate-100">
                <Button variant="outline" size="sm">← Previous Turn</Button>
                <Button variant="primary" size="sm">Next Turn &gt;</Button>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  )
}
