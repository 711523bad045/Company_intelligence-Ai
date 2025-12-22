import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function App() {
  const [companies, setCompanies] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [groupBy, setGroupBy] = useState("industry");

  useEffect(() => {
    fetch("/company_profiles.json")
      .then((res) => res.json())
      .then((data) => setCompanies(data))
      .catch(console.error);
  }, []);

  const filtered = companies.filter(
    (c) =>
      c.company_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.domain?.toLowerCase().includes(search.toLowerCase()) ||
      c.industry?.toLowerCase().includes(search.toLowerCase()) ||
      c.sector?.toLowerCase().includes(search.toLowerCase()) ||
      c.tags?.toLowerCase().includes(search.toLowerCase())
  );

  const categoryCount = {};
  companies.forEach((c) => {
    let category = c[groupBy]?.trim();
    if (!category || category.length < 2) category = "Unknown";
    categoryCount[category] = (categoryCount[category] || 0) + 1;
  });

  const sortedCategories = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const chartData = {
    labels: sortedCategories.map(([name]) => name),
    datasets: [
      {
        label: `Companies per ${groupBy.replace("_", " ")}`,
        data: sortedCategories.map(([, count]) => count),
        backgroundColor: "rgba(99, 102, 241, 0.8)",
        borderRadius: 8,
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { 
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        padding: 12,
        titleFont: { size: 14 },
        bodyFont: { size: 13 },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#64748b", maxRotation: 45, minRotation: 45, font: { size: 11 } },
      },
      y: {
        grid: { color: "#f1f5f9" },
        ticks: { color: "#64748b", stepSize: 1 },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={styles.pageWrapper}>
      <div style={styles.container}>
        {/* HEADER */}
        <div style={styles.header}>
          <div style={styles.headerContent}>
            <div style={styles.iconBadge}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" rx="1"/>
                <rect x="14" y="3" width="7" height="7" rx="1"/>
                <rect x="14" y="14" width="7" height="7" rx="1"/>
                <rect x="3" y="14" width="7" height="7" rx="1"/>
              </svg>
            </div>
            <div>
              <h1 style={styles.title}>Company Intelligence Hub</h1>
              <p style={styles.subtitle}>
                <span style={styles.countBadge}>{companies.length}</span> Companies Analyzed
              </p>
            </div>
          </div>
        </div>

        {/* GRAPH */}
        <div style={styles.chartBox}>
          <div style={styles.chartHeader}>
            <div>
              <h3 style={styles.chartTitle}>Distribution Analysis</h3>
              <p style={styles.chartSubtitle}>Top 10 categories by volume</p>
            </div>
            <select
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
              style={styles.select}
            >
              <option value="industry">Industry</option>
              <option value="sector">Sector</option>
            </select>
          </div>
          <div style={{ height: "300px" }}>
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>

        {/* SEARCH */}
        <div style={styles.searchContainer}>
          <div style={styles.searchWrapper}>
            <svg style={styles.searchIcon} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies, industries, sectors, or tags..."
              style={styles.searchInput}
            />
          </div>
          <div style={styles.resultCount}>
            Showing {filtered.length} of {companies.length} companies
          </div>
        </div>

        {/* TABLE */}
        <div style={styles.tableContainer}>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.headerRow}>
                  <th style={styles.thLogo}>Logo</th>
                  <th style={styles.th}>Company</th>
                  <th style={styles.th}>Sector</th>
                  <th style={styles.th}>Industry</th>
                  <th style={styles.thSmall}>SIC</th>
                  <th style={styles.th}>Tags</th>
                  <th style={styles.thAction}>Action</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((c, i) => (
                  <tr key={i} style={styles.row}>
                    <td style={styles.logoCell}>
                      {c.logo ? (
                        <img
                          src={c.logo}
                          alt=""
                          width="32"
                          height="32"
                          style={styles.logoImg}
                          onError={(e) => (e.target.style.display = "none")}
                        />
                      ) : (
                        <div style={styles.logoPlaceholder}>
                          {c.company_name?.[0] || "?"}
                        </div>
                      )}
                    </td>
                    <td style={styles.td}>
                      <div style={styles.companyCell}>
                        <strong style={styles.companyName}>{c.company_name || "-"}</strong>
                        <small style={styles.domain}>{c.domain}</small>
                      </div>
                    </td>
                    <td style={styles.td}>
                      <span style={styles.badge}>{c.sector || "-"}</span>
                    </td>
                    <td style={styles.td}>
                      <span style={styles.industryText}>{c.industry || "-"}</span>
                    </td>
                    <td style={styles.td}>
                      <code style={styles.code}>{c.sic_code || "-"}</code>
                    </td>
                    <td style={styles.td}>
                      <div style={styles.tags}>
                        {c.tags ? c.tags.split(",").slice(0, 2).map((tag, idx) => (
                          <span key={idx} style={styles.tag}>{tag.trim()}</span>
                        )) : <span style={styles.noData}>-</span>}
                      </div>
                    </td>
                    <td style={styles.td}>
                      <button
                        onClick={() => setSelectedCompany(c)}
                        style={styles.detailsBtn}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filtered.length === 0 && (
              <div style={styles.noResults}>
                <div style={styles.noResultsIcon}>🔍</div>
                <h3 style={styles.noResultsTitle}>No companies found</h3>
                <p style={styles.noResultsText}>Try adjusting your search criteria</p>
              </div>
            )}
          </div>
        </div>

        {/* MODAL */}
        {selectedCompany && (
          <div style={styles.modal} onClick={() => setSelectedCompany(null)}>
            <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <button
                style={styles.closeBtn}
                onClick={() => setSelectedCompany(null)}
              >
                ×
              </button>

              <div style={styles.modalHeader}>
                <div style={styles.modalHeaderContent}>
                  {selectedCompany.logo ? (
                    <img
                      src={selectedCompany.logo}
                      alt=""
                      width="56"
                      height="56"
                      style={styles.modalLogo}
                    />
                  ) : (
                    <div style={styles.modalLogoPlaceholder}>
                      {selectedCompany.company_name?.[0] || "?"}
                    </div>
                  )}
                  <div style={styles.modalHeaderText}>
                    <h2 style={styles.modalTitle}>{selectedCompany.company_name}</h2>
                    <p style={styles.modalDomain}>{selectedCompany.domain}</p>
                  </div>
                </div>
              </div>

              <div style={styles.modalBody}>
                <section style={styles.section}>
                  <h4 style={styles.sectionTitle}>📝 Description</h4>
                  <p style={styles.descriptionText}>
                    {selectedCompany.long_description || selectedCompany.short_description || "No description available"}
                  </p>
                </section>

                <section style={styles.section}>
                  <h4 style={styles.sectionTitle}>🏢 Business Classification</h4>
                  <div style={styles.grid}>
                    <div style={styles.gridItem}>
                      <div style={styles.gridLabel}>Sector</div>
                      <div style={styles.gridValue}>{selectedCompany.sector || "-"}</div>
                    </div>
                    <div style={styles.gridItem}>
                      <div style={styles.gridLabel}>Industry</div>
                      <div style={styles.gridValue}>{selectedCompany.industry || "-"}</div>
                    </div>
                    <div style={styles.gridItem}>
                      <div style={styles.gridLabel}>Sub-Industry</div>
                      <div style={styles.gridValue}>{selectedCompany.sub_industry || "-"}</div>
                    </div>
                    <div style={styles.gridItem}>
                      <div style={styles.gridLabel}>SIC Code</div>
                      <div style={styles.gridValue}>
                        <code style={styles.sicCode}>{selectedCompany.sic_code || "-"}</code>
                      </div>
                    </div>
                  </div>
                  {selectedCompany.sic_text && (
                    <div style={styles.sicTextBox}>
                      <em>{selectedCompany.sic_text}</em>
                    </div>
                  )}
                </section>

                {selectedCompany.tags && (
                  <section style={styles.section}>
                    <h4 style={styles.sectionTitle}>🏷️ Tags</h4>
                    <div style={styles.tagsList}>
                      {selectedCompany.tags.split(",").map((tag, idx) => (
                        <span key={idx} style={styles.tagLarge}>{tag.trim()}</span>
                      ))}
                    </div>
                  </section>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  pageWrapper: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    padding: "0",
    margin: "0",
    width: "100%",
    display: "flex",
    justifyContent: "center",
    paddingLeft: "40px",
  },
  container: {
    width: "100%",
    maxWidth: "1400px",
    padding: "40px 24px",
    margin: "0 auto",
    marginLeft: "auto",
    marginRight: "auto",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  header: {
    background: "rgba(255, 255, 255, 0.15)",
    backdropFilter: "blur(10px)",
    borderRadius: "16px",
    padding: "32px",
    marginBottom: "32px",
    border: "1px solid rgba(255, 255, 255, 0.2)",
  },
  headerContent: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
  },
  iconBadge: {
    width: "64px",
    height: "64px",
    background: "rgba(255, 255, 255, 0.2)",
    borderRadius: "16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: "36px",
    color: "#fff",
    margin: "0 0 8px 0",
    fontWeight: "700",
    letterSpacing: "-0.5px",
  },
  subtitle: {
    color: "rgba(255, 255, 255, 0.9)",
    fontSize: "16px",
    margin: "0",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  countBadge: {
    background: "#FFD700",
    color: "#1e293b",
    padding: "4px 12px",
    borderRadius: "20px",
    fontWeight: "700",
    fontSize: "16px",
  },

  chartBox: {
    background: "#ffffff",
    padding: "28px",
    borderRadius: "16px",
    marginBottom: "32px",
    boxShadow: "0 4px 24px rgba(0, 0, 0, 0.08)",
  },
  chartHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "24px",
  },
  chartTitle: {
    fontSize: "20px",
    fontWeight: "700",
    color: "#1e293b",
    margin: "0 0 4px 0",
  },
  chartSubtitle: {
    fontSize: "14px",
    color: "#64748b",
    margin: "0",
  },
  select: {
    padding: "10px 16px",
    borderRadius: "8px",
    border: "2px solid #e2e8f0",
    fontSize: "14px",
    cursor: "pointer",
    fontWeight: "500",
    color: "#475569",
    background: "#fff",
    transition: "all 0.2s",
  },

  searchContainer: {
    marginBottom: "24px",
  },
  searchWrapper: {
    position: "relative",
    maxWidth: "700px",
    margin: "0 auto 12px",
  },
  searchIcon: {
    position: "absolute",
    left: "16px",
    top: "50%",
    transform: "translateY(-50%)",
    pointerEvents: "none",
  },
  searchInput: {
    width: "100%",
    padding: "14px 16px 14px 48px",
    borderRadius: "12px",
    border: "2px solid rgba(255, 255, 255, 0.3)",
    fontSize: "15px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    background: "rgba(255, 255, 255, 0.95)",
    backdropFilter: "blur(10px)",
    transition: "all 0.2s",
    outline: "none",
    color: "#1e293b",
  },
  resultCount: {
    textAlign: "center",
    color: "rgba(255, 255, 255, 0.9)",
    fontSize: "14px",
    fontWeight: "500",
  },

  tableContainer: {
    background: "#ffffff",
    borderRadius: "16px",
    boxShadow: "0 4px 24px rgba(0,0,0,0.1)",
    overflow: "hidden",
  },
  tableWrapper: {
    overflowX: "auto",
  },

  table: { width: "100%", borderCollapse: "collapse" },
  headerRow: {
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
  },
  th: {
    padding: "18px 16px",
    color: "#ffffff",
    textAlign: "left",
    fontSize: "13px",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  thLogo: {
    padding: "18px 16px",
    color: "#ffffff",
    textAlign: "center",
    fontSize: "13px",
    fontWeight: "600",
    width: "60px",
  },
  thSmall: {
    padding: "18px 16px",
    color: "#ffffff",
    textAlign: "left",
    fontSize: "13px",
    fontWeight: "600",
    width: "80px",
  },
  thAction: {
    padding: "18px 16px",
    color: "#ffffff",
    textAlign: "center",
    fontSize: "13px",
    fontWeight: "600",
    width: "140px",
  },

  row: {
    borderBottom: "1px solid #f1f5f9",
    transition: "background 0.2s",
  },
  td: {
    padding: "16px",
    color: "#1e293b",
    background: "#fff",
    fontSize: "14px",
  },

  logoCell: {
    padding: "12px",
    background: "#fff",
    textAlign: "center",
  },
  logoImg: {
    borderRadius: "8px",
    objectFit: "contain",
  },
  logoPlaceholder: {
    width: "32px",
    height: "32px",
    borderRadius: "8px",
    background: "linear-gradient(135deg, #667eea, #764ba2)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "14px",
    fontWeight: "700",
    margin: "0 auto",
  },

  companyCell: { display: "flex", flexDirection: "column", gap: "4px" },
  companyName: { color: "#1e293b", fontSize: "14px" },
  domain: { color: "#64748b", fontSize: "12px" },

  badge: {
    display: "inline-block",
    padding: "6px 12px",
    background: "#f1f5f9",
    borderRadius: "8px",
    fontSize: "12px",
    fontWeight: "600",
    color: "#475569",
  },
  industryText: { color: "#475569", fontSize: "14px" },

  code: {
    background: "#f8fafc",
    padding: "4px 8px",
    borderRadius: "6px",
    fontSize: "12px",
    fontFamily: "'Fira Code', monospace",
    fontWeight: "600",
    color: "#6366f1",
    border: "1px solid #e2e8f0",
  },

  tags: { display: "flex", gap: "6px", flexWrap: "wrap" },
  tag: {
    background: "#ede9fe",
    padding: "4px 10px",
    borderRadius: "6px",
    fontSize: "11px",
    color: "#7c3aed",
    fontWeight: "500",
  },
  noData: { color: "#cbd5e1", fontSize: "13px" },

  detailsBtn: {
    padding: "8px 16px",
    background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "13px",
    fontWeight: "600",
    transition: "transform 0.2s, box-shadow 0.2s",
    boxShadow: "0 2px 8px rgba(99, 102, 241, 0.3)",
  },

  noResults: {
    padding: "60px 20px",
    textAlign: "center",
  },
  noResultsIcon: { fontSize: "48px", marginBottom: "16px" },
  noResultsTitle: {
    fontSize: "20px",
    color: "#1e293b",
    margin: "0 0 8px 0",
    fontWeight: "600",
  },
  noResultsText: { fontSize: "14px", color: "#64748b", margin: "0" },

  modal: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0, 0, 0, 0.75)",
    backdropFilter: "blur(4px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: "20px",
  },
  modalContent: {
    background: "white",
    borderRadius: "20px",
    maxWidth: "700px",
    width: "100%",
    maxHeight: "90vh",
    overflow: "auto",
    position: "relative",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
  },
  closeBtn: {
    position: "absolute",
    top: "20px",
    right: "20px",
    background: "#f1f5f9",
    border: "none",
    borderRadius: "50%",
    width: "36px",
    height: "36px",
    fontSize: "24px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#64748b",
    fontWeight: "300",
    transition: "all 0.2s",
    zIndex: 10,
  },
  modalHeader: {
    padding: "36px",
    borderBottom: "1px solid #f1f5f9",
    background: "linear-gradient(135deg, #f8fafc 0%, #fff 100%)",
  },
  modalHeaderContent: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
  },
  modalLogo: {
    borderRadius: "12px",
    objectFit: "contain",
  },
  modalLogoPlaceholder: {
    width: "56px",
    height: "56px",
    borderRadius: "12px",
    background: "linear-gradient(135deg, #667eea, #764ba2)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "24px",
    fontWeight: "700",
  },
  modalHeaderText: { flex: 1 },
  modalTitle: { margin: "0", fontSize: "28px", color: "#1e293b", fontWeight: "700" },
  modalDomain: { margin: "6px 0 0 0", color: "#64748b", fontSize: "15px" },
  modalBody: { padding: "36px" },
  section: { marginBottom: "32px" },
  sectionTitle: {
    fontSize: "16px",
    fontWeight: "700",
    marginBottom: "16px",
    color: "#1e293b",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  descriptionText: {
    fontSize: "15px",
    lineHeight: "1.7",
    color: "#475569",
    margin: "0",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
    marginBottom: "12px",
  },
  gridItem: {
    background: "#f8fafc",
    padding: "16px",
    borderRadius: "12px",
    border: "1px solid #e2e8f0",
  },
  gridLabel: {
    fontSize: "12px",
    color: "#64748b",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    marginBottom: "6px",
  },
  gridValue: {
    fontSize: "15px",
    color: "#1e293b",
    fontWeight: "600",
  },
  sicCode: {
    background: "#fff",
    padding: "4px 10px",
    borderRadius: "6px",
    fontSize: "13px",
    fontFamily: "'Fira Code', monospace",
    fontWeight: "700",
    color: "#6366f1",
    border: "1px solid #e2e8f0",
  },
  sicTextBox: {
    background: "#f8fafc",
    padding: "14px",
    borderRadius: "8px",
    fontSize: "13px",
    color: "#64748b",
    marginTop: "12px",
  },
  tagsList: { display: "flex", gap: "8px", flexWrap: "wrap" },
  tagLarge: {
    background: "#ede9fe",
    padding: "8px 16px",
    borderRadius: "10px",
    fontSize: "13px",
    color: "#7c3aed",
    fontWeight: "600",
  },
};

export default App;