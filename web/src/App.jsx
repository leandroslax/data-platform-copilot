import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1'
const DEFAULT_DATASET = 'samples.tpch.orders'
const IS_PUBLIC_DEMO = API_BASE.includes('run.app')

function App() {
  const [question, setQuestion] = useState('Quais colunas existem em samples.tpch.orders?')
  const [chat, setChat] = useState(null)
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')

  const [datasets, setDatasets] = useState([])
  const [datasetsLoading, setDatasetsLoading] = useState(true)
  const [datasetsError, setDatasetsError] = useState('')
  const [selectedDatasetId, setSelectedDatasetId] = useState(DEFAULT_DATASET)

  const [datasetDetail, setDatasetDetail] = useState(null)
  const [datasetLoading, setDatasetLoading] = useState(false)
  const [datasetError, setDatasetError] = useState('')

  const [jobs, setJobs] = useState([])
  const [jobsLoading, setJobsLoading] = useState(true)
  const [jobsError, setJobsError] = useState('')
  const [searchQuery, setSearchQuery] = useState('owner sales-platform')
  const [searchResults, setSearchResults] = useState([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState('')

  useEffect(() => {
    loadDatasets()
    loadJobs()
    searchCatalog('owner sales-platform')
  }, [])

  useEffect(() => {
    if (selectedDatasetId) {
      loadDatasetDetail(selectedDatasetId)
    }
  }, [selectedDatasetId])

  const featuredDatasets = useMemo(() => {
    if (!datasets.length) return []
    const featured = datasets.find((dataset) => dataset.dataset_id === DEFAULT_DATASET)
    const remaining = datasets.filter((dataset) => dataset.dataset_id !== DEFAULT_DATASET)
    return featured ? [featured, ...remaining].slice(0, 8) : datasets.slice(0, 8)
  }, [datasets])

  async function loadDatasets() {
    setDatasetsLoading(true)
    setDatasetsError('')

    try {
      const response = await fetch(`${API_BASE}/datasets`)
      if (!response.ok) {
        throw new Error(`datasets request failed: ${response.status}`)
      }

      const data = await response.json()
      setDatasets(data.items || [])

      const datasetIds = (data.items || []).map((item) => item.dataset_id)
      if (datasetIds.includes(DEFAULT_DATASET)) {
        setSelectedDatasetId(DEFAULT_DATASET)
      } else if (!selectedDatasetId && data.items?.length) {
        setSelectedDatasetId(data.items[0].dataset_id)
      }
    } catch (error) {
      console.error(error)
      setDatasetsError(String(error))
    } finally {
      setDatasetsLoading(false)
    }
  }

  async function loadDatasetDetail(datasetId) {
    setDatasetLoading(true)
    setDatasetError('')

    try {
      const response = await fetch(`${API_BASE}/datasets/${encodeURIComponent(datasetId)}`)
      if (!response.ok) {
        throw new Error(`dataset detail request failed: ${response.status}`)
      }

      const data = await response.json()
      setDatasetDetail(data)
    } catch (error) {
      console.error(error)
      setDatasetError(String(error))
    } finally {
      setDatasetLoading(false)
    }
  }

  async function loadJobs() {
    setJobsLoading(true)
    setJobsError('')

    try {
      const response = await fetch(`${API_BASE}/jobs`)
      if (!response.ok) {
        throw new Error(`jobs request failed: ${response.status}`)
      }

      const data = await response.json()
      setJobs(data.items || [])
    } catch (error) {
      console.error(error)
      setJobsError(String(error))
    } finally {
      setJobsLoading(false)
    }
  }

  async function askChat(event) {
    event.preventDefault()
    setChatLoading(true)
    setChat(null)
    setChatError('')

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!response.ok) {
        throw new Error(`chat request failed: ${response.status}`)
      }

      const data = await response.json()
      setChat(data)
    } catch (error) {
      console.error(error)
      setChatError(String(error))
    } finally {
      setChatLoading(false)
    }
  }

  async function searchCatalog(query = searchQuery) {
    if (!query.trim()) return

    setSearchLoading(true)
    setSearchError('')

    try {
      const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=6`)
      if (!response.ok) {
        throw new Error(`search request failed: ${response.status}`)
      }

      const data = await response.json()
      setSearchResults(data.items || [])
    } catch (error) {
      console.error(error)
      setSearchError(String(error))
    } finally {
      setSearchLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Data Platform Copilot</p>
          <h1>Metadata, lineage and incidents in one place.</h1>
          <p className="hero-copy">
            Demo UI for the FastAPI backend running on Cloud Run with Databricks-backed dataset discovery.
          </p>
          <div className="hero-badges">
            <span className="hero-badge">{IS_PUBLIC_DEMO ? 'Demo publico' : 'Ambiente local'}</span>
            <span className="hero-badge hero-badge-muted">{API_BASE}</span>
          </div>
        </div>

        <div className="hero-card">
          <span className="hero-card-label">Featured dataset</span>
          <h2>{datasetDetail?.dataset_id || DEFAULT_DATASET}</h2>
          <p>{datasetDetail?.description || 'Databricks-backed metadata exploration with live dataset detail and chat.'}</p>
          <div className="hero-stats">
            <div>
              <strong>{datasetDetail?.columns?.length || 0}</strong>
              <span>columns</span>
            </div>
            <div>
              <strong>{datasetDetail?.owner || 'N/A'}</strong>
              <span>owner</span>
            </div>
            <div>
              <strong>{jobs.length}</strong>
              <span>jobs</span>
            </div>
          </div>
        </div>
      </header>

      <main className="grid">
        <section className="panel panel-chat">
          <div className="panel-heading">
            <h2>Chat</h2>
            <span className="panel-kicker">Ask about datasets, columns and jobs</span>
          </div>

          <form onSubmit={askChat} className="chat-form">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={4}
              placeholder="Pergunte sobre datasets, colunas, lineage ou jobs"
            />
            <div className="chat-actions">
              <button type="submit" disabled={chatLoading}>
                {chatLoading ? 'Consultando...' : 'Perguntar'}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setQuestion('Quais colunas existem em samples.tpch.orders?')}
              >
                Usar exemplo
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setQuestion('Quais datasets pertencem ao owner sales-platform?')}
              >
                Perguntar por owner
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setQuestion('Compare o faturamento da Novadrive entre a ultima semana e a semana anterior')}
              >
                Comparar semanas
              </button>
            </div>
          </form>

          {chatError && <p className="error-text">{chatError}</p>}

          {chat && (
            <div className="chat-response-card">
              <div className="chat-response-header">
                <span className="chat-response-label">Latest answer</span>
              </div>
              <p className="chat-response-text">{chat.answer}</p>
              <div className="chips">
                {chat.sources.map((source) => (
                  <span key={`${source.type}-${source.id}`} className="chip">
                    {source.type}: {source.id}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="panel panel-detail">
          <div className="panel-heading">
            <h2>Dataset Detail</h2>
            <span className="panel-kicker">Columns and metadata</span>
          </div>

          {datasetLoading && <p>Carregando detalhe...</p>}
          {datasetError && <p className="error-text">{datasetError}</p>}

          {!datasetLoading && !datasetError && datasetDetail && (
            <>
              <div className="detail-meta">
                <div className="meta-card">
                  <span>ID</span>
                  <strong>{datasetDetail.dataset_id}</strong>
                </div>
                <div className="meta-card">
                  <span>Owner</span>
                  <strong>{datasetDetail.owner || 'N/A'}</strong>
                </div>
              <div className="meta-card">
                <span>Type</span>
                <strong>{datasetDetail.type}</strong>
              </div>
                <div className="meta-card">
                  <span>Schema</span>
                  <strong>{datasetDetail.schema || 'N/A'}</strong>
                </div>
              </div>

              <h3>Columns</h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Nullable</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datasetDetail.columns?.length ? (
                      datasetDetail.columns.map((column) => (
                        <tr key={column.name}>
                          <td>{column.name}</td>
                          <td>{column.data_type || 'N/A'}</td>
                          <td>{String(column.nullable)}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="3">Nenhuma coluna encontrada.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Datasets</h2>
            <span className="panel-kicker">Top entries from the API</span>
          </div>

          {datasetsLoading && <p>Carregando datasets...</p>}
          {datasetsError && <p className="error-text">{datasetsError}</p>}

          {!datasetsLoading && !datasetsError && (
            <div className="dataset-list">
              {featuredDatasets.map((dataset) => (
                <button
                  key={dataset.dataset_id}
                  className={`dataset-item ${selectedDatasetId === dataset.dataset_id ? 'active' : ''}`}
                  onClick={() => setSelectedDatasetId(dataset.dataset_id)}
                >
                  <strong>{dataset.dataset_id}</strong>
                  <span>{dataset.owner || 'Sem owner'}</span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Busca Semantica</h2>
            <span className="panel-kicker">Catalogo persistido + embeddings</span>
          </div>

          <form
            className="search-form"
            onSubmit={(event) => {
              event.preventDefault()
              searchCatalog()
            }}
          >
            <input
              type="text"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Ex.: owner data-platform, runbook airflow ou novadrive previsao"
            />
            <button type="submit" disabled={searchLoading}>
              {searchLoading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>

          {searchError && <p className="error-text">{searchError}</p>}

          {!searchError && (
            <div className="search-results">
              {searchResults.map((item) => (
                <button
                  key={item.item_id || item.dataset_id}
                  className="dataset-item"
                  onClick={() => {
                    if (item.item_type === 'document') {
                      setQuestion(`Resuma o documento ${item.name}`)
                      return
                    }
                    if (item.dataset_id) {
                      setSelectedDatasetId(item.dataset_id)
                    }
                  }}
                >
                  <strong>{item.dataset_id || item.name}</strong>
                  <span>
                    {item.item_type === 'document'
                      ? `${item.path || 'documentacao'} • score ${Number(item.score).toFixed(2)}`
                      : `${item.owner || 'Sem owner'} • score ${Number(item.score).toFixed(2)}`}
                  </span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Jobs</h2>
            <span className="panel-kicker">Operational snapshot</span>
          </div>

          {jobsLoading && <p>Carregando jobs...</p>}
          {jobsError && <p className="error-text">{jobsError}</p>}

          {!jobsLoading && !jobsError && (
            <div className="job-list">
              {jobs.map((job) => (
                <div key={job.job_id} className="job-item">
                  <div>
                    <strong>{job.job_name}</strong>
                    <span>{job.job_id}</span>
                  </div>
                  <span className={`status status-${(job.status || 'unknown').toLowerCase()}`}>
                    {job.status || 'unknown'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
