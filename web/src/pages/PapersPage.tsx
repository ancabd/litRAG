import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAddPdf, usePapers, useMeta, type PaperFilters } from "../api/hooks";
import { CopyId, ErrorBanner, SearchIcon, Seg, StatusPill, Empty, Toast, useDebounced, useToast } from "../components/ui";

const PAGE = 50;

/** Filters live in the URL, so back/forward and reloads keep them. */
function useFilters(): [PaperFilters, (patch: Partial<PaperFilters>) => void] {
  const [params, setParams] = useSearchParams();
  const f: PaperFilters = {
    q: params.get("q") ?? "",
    status: params.get("status") ?? "",
    role: params.get("role") ?? "",
    seed: params.get("seed") ?? "",
    sort: params.get("sort") ?? "cited",
    offset: Number(params.get("offset") ?? 0),
    limit: PAGE,
  };
  const set = (patch: Partial<PaperFilters>) => {
    const next = { ...f, offset: 0, ...patch };
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(next)) {
      if (k === "limit" || v === "" || (k === "sort" && v === "cited") || (k === "offset" && v === 0)) continue;
      p.set(k, String(v));
    }
    setParams(p, { replace: true });
  };
  return [f, set];
}

export function PapersPage() {
  const [f, set] = useFilters();
  const papers = usePapers(f);
  const meta = useMeta();
  const navigate = useNavigate();
  const data = papers.data;
  const counts = data?.status_counts ?? {};
  const all = Object.values(counts).reduce((a, b) => a + b, 0);
  const [text, setText] = useState(f.q);
  // adding PDFs from the list: one hidden file input, aimed at whichever row asked
  const addPdf = useAddPdf();
  const fileInput = useRef<HTMLInputElement>(null);
  const target = useRef<string | null>(null);
  const [dropRow, setDropRow] = useState<string | null>(null);
  const [toast, showToast] = useToast();
  const upload = (paperId: string, file: File | undefined) => {
    if (!file) return;
    if (!(file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf"))) {
      showToast("That isn't a PDF file.");
      return;
    }
    addPdf.mutate(
      { paperId, file },
      {
        onSuccess: (res) => {
          const failed = res.ingest.find((r) => r.error);
          const n = res.ingest[0]?.n_chunks;
          showToast(failed ? `Saved, but the PDF couldn't be parsed. Open the paper for details.`
            : `Added the PDF${n ? `: ${n} chunks` : ""}.`);
        },
        onError: (e) => showToast(e.message),
      },
    );
  };
  const debounced = useDebounced(text, 250);
  useEffect(() => {
    if (debounced !== f.q) set({ q: debounced });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);

  if (meta.data && !meta.data.corpus.available) {
    return (
      <div className="page">
        <Empty title="No corpus yet">
          <p>
            Build one with <code>python corpus_builder.py seeds.txt</code> in corpus-builder. The app looks for{" "}
            <code>{meta.data.paths.corpus_dir}/manifest.jsonl</code>.
          </p>
        </Empty>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Papers</h1>
          <p className="sub">Everything the corpus builder collected: seeds, the papers they cite, and the papers citing them.</p>
        </div>
      </div>

      <div className="toolbar">
        <div className="search-input">
          <SearchIcon />
          <input
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Title, author, venue, year or W… id"
            aria-label="Search papers"
          />
        </div>
        <select className="select" value={f.role} onChange={(e) => set({ role: e.target.value })} aria-label="Role">
          <option value="">All roles</option>
          <option value="seed">Seeds</option>
          <option value="reference">Cited by a seed</option>
          <option value="citing">Citing a seed</option>
        </select>
        <select className="select" value={f.seed} onChange={(e) => set({ seed: e.target.value })} aria-label="Found via seed">
          <option value="">Via any seed</option>
          {meta.data?.corpus.seeds.map((s) => (
            <option key={s.openalex_id} value={s.openalex_id}>
              Via {s.title && s.title.length > 48 ? `${s.title.slice(0, 48)}…` : s.title}
            </option>
          ))}
        </select>
        <select className="select" value={f.sort} onChange={(e) => set({ sort: e.target.value })} aria-label="Sort">
          <option value="cited">Most cited</option>
          <option value="year">Newest</option>
          <option value="year_asc">Oldest</option>
          <option value="title">Title</option>
        </select>
      </div>
      <div className="toolbar">
        <Seg
          label="Full text status"
          value={f.status}
          onChange={(status) => set({ status })}
          options={[
            { value: "", label: "All", n: all },
            { value: "pdf", label: "Full text", n: counts.pdf ?? 0 },
            { value: "abstract_only", label: "Abstract only", n: counts.abstract_only ?? 0 },
            { value: "metadata_only", label: "Metadata only", n: counts.metadata_only ?? 0 },
          ]}
        />
      </div>

      {papers.error && <ErrorBanner error={papers.error} />}
      {(f.status === "abstract_only" || f.status === "metadata_only") && (
        <p className="small muted" style={{ margin: "-4px 0 12px" }}>
          Have some of these as PDFs? Drop a file onto its row, or use Add PDF.
        </p>
      )}
      <input
        ref={fileInput}
        type="file"
        accept="application/pdf,.pdf"
        hidden
        onChange={(e) => {
          if (target.current) upload(target.current, e.target.files?.[0]);
          e.target.value = "";
        }}
      />

      {data && (
        <>
          <div className="table-wrap" style={{ opacity: papers.isPlaceholderData ? 0.6 : 1 }}>
            <table className="data">
              <thead>
                <tr>
                  <th>Paper</th>
                  <th>Year</th>
                  <th>Status</th>
                  <th className="num hide-sm" title="Chunks in the selected run">Chunks</th>
                  <th className="num hide-sm">Cited by</th>
                  <th className="hide-sm">Id</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((p) => (
                  <tr
                    key={p.openalex_id}
                    className={dropRow === p.openalex_id ? "drop-over" : ""}
                    onClick={() => navigate(`/papers/${p.openalex_id}`)}
                    onDragOver={(e) => {
                      if (p.status === "pdf" && !p.added_manually.includes("pdf")) return;
                      e.preventDefault();
                      setDropRow(p.openalex_id);
                    }}
                    onDragLeave={() => setDropRow(null)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setDropRow(null);
                      upload(p.openalex_id, e.dataTransfer.files[0]);
                    }}
                  >
                    <td>
                      <a
                        className="paper-title"
                        href={`/papers/${p.openalex_id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          navigate(`/papers/${p.openalex_id}`);
                        }}
                      >
                        {p.title ?? "Untitled"}
                      </a>
                      <div className="paper-meta">
                        {p.authors}
                        {p.venue && <>, {p.venue}</>}
                        {p.roles?.includes("seed") && (
                          <span className="pill accent" style={{ marginLeft: 8 }}>
                            seed
                          </span>
                        )}
                      </div>
                    </td>
                    <td>{p.year ?? ""}</td>
                    <td>
                      <StatusPill status={p.status} />
                      {p.added_manually.includes("pdf") && <div className="xs muted row-action">added by you</div>}
                      {p.status !== "pdf" && (
                        <div className="row-action">
                          <button
                            type="button"
                            className="btn small"
                            disabled={addPdf.isPending}
                            onClick={(e) => {
                              e.stopPropagation();
                              target.current = p.openalex_id;
                              fileInput.current?.click();
                            }}
                          >
                            {addPdf.isPending && addPdf.variables?.paperId === p.openalex_id ? "Adding…" : "Add PDF"}
                          </button>
                        </div>
                      )}
                    </td>
                    <td className="num hide-sm">{p.n_chunks ?? ""}</td>
                    <td className="num hide-sm">{p.cited_by_count?.toLocaleString() ?? ""}</td>
                    <td className="hide-sm">
                      <CopyId id={p.openalex_id} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data.items.length === 0 && <p className="muted small" style={{ padding: 16 }}>No papers match.</p>}
          </div>
          <div className="pager">
            <span>
              {data.total === 0 ? 0 : data.offset + 1}–{Math.min(data.offset + PAGE, data.total)} of {data.total}
            </span>
            <button type="button" className="btn small" disabled={data.offset === 0} onClick={() => set({ offset: Math.max(0, f.offset - PAGE) })}>
              Previous
            </button>
            <button type="button" className="btn small" disabled={data.offset + PAGE >= data.total} onClick={() => set({ offset: f.offset + PAGE })}>
              Next
            </button>
          </div>
        </>
      )}
      <Toast message={toast} />
    </div>
  );
}
