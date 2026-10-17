import React, { useState, useEffect } from 'react';
import {
  EvaluationRun,
  QualityGateRule,
  RegressionComparison,
  TestSuite,
} from './types/evalgate';
import {
  executeEvaluationRun,
  fetchGateRules,
  fetchRegressionComparison,
  fetchRuns,
  fetchSuites,
} from './lib/api';
import { Header } from './components/Header';
import { CiMatrixTab } from './components/CiMatrixTab';
import { StatsTab } from './components/StatsTab';
import { GateRulesTab } from './components/GateRulesTab';
import { LabTab } from './components/LabTab';
import {
  BarChart3,
  SlidersHorizontal,
  FlaskConical,
  ShieldCheck,
  Activity,
  Layers,
  FolderUp,
} from 'lucide-react';
import { FileUploadZone } from './components/FileUploadZone';

export function App() {
  const [activeTab, setActiveTab] = useState<'matrix' | 'stats' | 'rules' | 'lab' | 'datasets'>('matrix');
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [rules, setRules] = useState<QualityGateRule[]>([]);
  const [comparison, setComparison] = useState<RegressionComparison | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [executing, setExecuting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [suitesData, runsData, rulesData] = await Promise.all([
        fetchSuites(),
        fetchRuns(),
        fetchGateRules(),
      ]);
      setSuites(suitesData);
      setRuns(runsData);
      setRules(rulesData);

      // Default compare baseline vs candidate
      if (runsData.length >= 2) {
        const comp = await fetchRegressionComparison(runsData[0].id, runsData[1].id);
        setComparison(comp);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load EvalGate telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExecuteBenchmark = async () => {
    if (suites.length === 0) return;
    try {
      setExecuting(true);
      const newRun = await executeEvaluationRun({
        suite_id: suites[0].id,
        label: `Candidate Run (Live GPU ${new Date().toLocaleTimeString()})`,
        model: suites[0].default_model || 'qwen2.5:0.5b',
      });
      // Re-compare against baseline
      const updatedRuns = await fetchRuns();
      setRuns(updatedRuns);
      if (updatedRuns.length >= 2) {
        const comp = await fetchRegressionComparison(updatedRuns[0].id, newRun.id);
        setComparison(comp);
      }
    } catch (err: any) {
      alert(`Benchmark execution failed: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <Header
        suites={suites}
        runs={runs}
        comparison={comparison}
        onExecuteSuite={handleExecuteBenchmark}
        executing={executing}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Navigation Tabs */}
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-slate-950 p-1">
            <button
              onClick={() => setActiveTab('matrix')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === 'matrix'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>CI Regression Matrix</span>
            </button>

            <button
              onClick={() => setActiveTab('stats')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === 'stats'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Activity className="h-4 w-4" />
              <span>Statistical Distributions & Significance</span>
            </button>

            <button
              onClick={() => setActiveTab('rules')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === 'rules'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <ShieldCheck className="h-4 w-4" />
              <span>Quality Gate Rules</span>
            </button>

            <button
              onClick={() => setActiveTab('lab')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === 'lab'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <FlaskConical className="h-4 w-4" />
              <span>Live Test Assertion Lab</span>
            </button>

            <button
              onClick={() => setActiveTab('datasets')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === 'datasets'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <FolderUp className="h-4 w-4" />
              <span>Test Datasets Upload</span>
            </button>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span>Telemetry Stream: Active</span>
          </div>
        </div>

        {/* Tab Views */}
        {loading ? (
          <div className="flex h-72 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/30">
            <div className="flex flex-col items-center gap-3">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
              <span className="text-xs text-slate-400 font-mono">
                Computing two-sample regression metrics...
              </span>
            </div>
          </div>
        ) : (
          <div>
            {activeTab === 'matrix' && <CiMatrixTab comparison={comparison} />}
            {activeTab === 'stats' && <StatsTab comparison={comparison} />}
            {activeTab === 'rules' && (
              <GateRulesTab
                comparison={comparison}
                rules={rules}
                report={comparison?.gate_report || null}
                onRefreshGates={loadData}
              />
            )}
            {activeTab === 'lab' && <LabTab />}
            {activeTab === 'datasets' && (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-100">Evaluation Datasets & Golden Answers</h3>
                  <p className="text-xs text-slate-400">
                    Upload evaluation test datasets (.csv, .jsonl, .json) to populate test cases and run automated regression gates.
                  </p>
                </div>
                <FileUploadZone
                  apiBaseUrl="/api/v1"
                  allowedExtensions={['.csv', '.jsonl', '.json', '.txt']}
                  acceptedFormatsText="CSV, JSONL, JSON, TXT"
                  onFileProcessed={() => {
                    loadData();
                  }}
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
