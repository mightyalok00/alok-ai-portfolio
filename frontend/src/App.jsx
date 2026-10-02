import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  BriefcaseBusiness,
  ExternalLink,
  Github,
  MessageSquare,
  Search,
  Send,
  Sparkles,
  Trash2,
  UserRound,
  X,
  AlertTriangle,
  CheckCircle2,
  FolderKanban,
} from "lucide-react";

const API = "";

const QUICK = [
  "Give me a concise recruiter summary of Alok.",
  "Which projects demonstrate Python?",
  "What documented evidence supports Alok's machine learning skills?",
  "What is documented about Alok's FastAPI work?",
];

const RECRUITER_PROMPTS = [
  ["Candidate snapshot", "Give me a concise recruiter summary of Alok using only documented portfolio evidence."],
  ["Technical strengths", "What technical skills are documented, and which projects provide evidence for them?"],
  ["Project fit", "Which documented projects are most relevant to a Python and machine learning role, and why?"],
  ["Evidence gaps", "What information is not currently verified in Alok's portfolio, such as education or employment?"],
  ["FastAPI evidence", "Explain the documented FastAPI work and point to the relevant project evidence."],
  ["GenAI evidence", "What Generative AI work is actually documented in the portfolio?"],
];

function ProjectCard({ project, onOpen }) {
  return (
    <article className="project-card">
      <div className="project-top"><span className="project-dot" /><span>PROJECT</span></div>
      <h3>{project.name}</h3>
      <p>{project.description}</p>
      <div className="chips">
        {(project.technologies || []).slice(0, 5).map((tech) => <span key={tech}>{tech}</span>)}
      </div>
      <div className="project-actions">
        <button className="project-detail-button" onClick={() => onOpen(project)}>View project</button>
        {project.repository && <a href={project.repository} target="_blank" rel="noreferrer"><Github size={15} /> GitHub</a>}
      </div>
    </article>
  );
}

function ResultBlock({ title, items = [], icon: Icon = CheckCircle2, tone = "default", compact = false }) {
  return (
    <section className={`result-block result-block-${tone}${compact ? " result-block-compact" : ""}`}>
      <div className="result-title"><Icon size={16} /><h3>{title}</h3><span>{items.length}</span></div>
      {items.length ? (
        <ul>{items.map((item, i) => <li key={`${item}-${i}`}>{item}</li>)}</ul>
      ) : <p className="empty-result">None returned.</p>}
    </section>
  );
}

function JdMetric({ value, label, icon: Icon }) {
  return (
    <div className="jd-metric">
      <span className="jd-metric-icon"><Icon size={16} /></span>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

export default function App() {
  const [candidate, setCandidate] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tab, setTab] = useState("home");
  const [messages, setMessages] = useState([{ role: "assistant", content: "Hi! I'm Alok's AI portfolio representative. Ask me about documented projects, technologies, or experience." }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [jd, setJd] = useState("");
  const [jdResult, setJdResult] = useState(null);
  const [focus, setFocus] = useState("machine learning");
  const [interview, setInterview] = useState(null);
  const [interviewAnswer, setInterviewAnswer] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);
  const [jdContext, setJdContext] = useState(null);
  const bottom = useRef(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/candidate`).then((r) => r.json()),
      fetch(`${API}/api/projects`).then((r) => r.json()),
      fetch(`${API}/api/health`).then((r) => r.json()),
    ]).then(([profile, projectList, health]) => {
      setCandidate(profile);
      setProjects(projectList);
      setApiHealth(health);
    }).catch(() => {});
  }, []);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function sendMessage(value = input) {
    const message = value.trim();
    if (!message || loading) return;
    const history = messages.slice(-8);
    setMessages((items) => [...items, { role: "user", content: message }, { role: "assistant", content: "" }]);
    setInput("");
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: groundedMessage, history }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          const event = JSON.parse(line);
          if (event.error) {
            throw new Error(event.error);
          }
          if (!event.token) continue;
          setMessages((items) => {
            const next = [...items];
            next[next.length - 1] = { role: "assistant", content: next[next.length - 1].content + event.token };
            return next;
          });
        }
      }
    } catch (error) {
      setMessages((items) => {
        const next = [...items];
        next[next.length - 1] = { role: "assistant", content: `I couldn't connect to the local portfolio API. ${error.message}` };
        return next;
      });
    } finally { setLoading(false); }
  }

  async function analyzeJD() {
    if (jd.trim().length < 20) return;
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/match-job`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jd }),
      });
      setJdResult(await response.json());
    } catch (error) {
      setJdResult({ notes: [`Could not analyze JD: ${error.message}`] });
    } finally { setLoading(false); }
  }

  async function startInterview(answer = "") {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/interview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ focus, previous_answer: answer, history: messages.slice(-6) }),
      });
      setInterview(await response.json());
      setInterviewAnswer("");
    } catch (error) {
      setInterview({ question: `Interview service error: ${error.message}` });
    } finally { setLoading(false); }
  }

  function clearChat() {
    setMessages([{ role: "assistant", content: "Chat cleared. Ask me about the documented portfolio." }]);
  }

  const projectCount = candidate?.projects?.length || projects.length || 0;
  const skillCount = candidate?.skills?.length || 0;
  const skills = candidate?.skills || [];
  const featured = projects.slice(0, 3);

  function openSkillEvidence(skill) {
    const evidence = projects.filter((p) =>
      (p.technologies || []).some((t) => t.toLowerCase() === skill.toLowerCase())
    );
    setSelectedSkill({ name: skill, projects: evidence });
  }

  return (
    <main className="app-shell">
      <nav className="nav">
        <button className="brand" onClick={() => setTab("home")}><span className="brand-mark">A</span><span>ALOK AI</span></button>
        <div className="nav-tabs">
          {[
            ["home", "Home"], ["recruiter", "Recruiter Mode"], ["projects", "Projects"],
            ["chat", "AI Chat"], ["jd", "JD Analyzer"], ["interview", "Interview"],
          ].map(([key, label]) => <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>{label}</button>)}
        </div>
        <a className="github-link" href="https://github.com/mightyalok00" target="_blank" rel="noreferrer"><Github size={17} /> GitHub</a>
      </nav>

      {tab === "home" && (
        <>
          <section className="hero">
            <div className="hero-copy">
              <div className="eyebrow"><Sparkles size={15} /> LOCAL AI PORTFOLIO</div>
              <h1>{candidate?.name || "Alok Agarwal"}</h1>
              <h2>{candidate?.headline || "Data Scientist & Python Developer"}</h2>
              <p>{candidate?.summary || "Explore documented data science, Python, machine learning, and AI projects."}</p>
              <div className="hero-actions">
                <button className="primary" onClick={() => setTab("recruiter")}><BriefcaseBusiness size={17} /> Recruiter Mode</button>
                <button className="secondary" onClick={() => setTab("chat")}><MessageSquare size={17} /> Chat with Alok AI</button>
              </div>
            </div>
            <div className="hero-profile">
              <img src="/profile.jpg" alt="Alok Agarwal" />
              <div className="profile-label"><strong>ALOK AGARWAL</strong><span>DATA SCIENTIST • PYTHON DEVELOPER</span></div>
            </div>
          </section>

          <section className="stats">
            <div><strong>{projectCount}+</strong><span>Projects</span></div>
            <div><strong>{skillCount}+</strong><span>Documented skills</span></div>
            <div><strong>3</strong><span>Local models</span></div>
            <div><strong>100%</strong><span>Local core AI</span></div>
          </section>

          <section className="section recruiter-banner">
            <div><div className="section-kicker">FOR RECRUITERS</div><h2>Find the evidence you need faster.</h2><p>Explore projects, inspect documented skills, analyze a job description, or start a portfolio-grounded interview.</p></div>
            <button className="primary" onClick={() => setTab("recruiter")}>Open Recruiter Mode →</button>
          </section>

          <section className="section">
            <div className="section-heading"><div><span className="section-kicker">FEATURED WORK</span><h2>Built with data, Python & AI</h2></div><button className="text-button" onClick={() => setTab("projects")}>View all →</button></div>
            <div className="project-grid">{featured.map((project) => <ProjectCard key={project.name} project={project} onOpen={setSelectedProject} />)}</div>
          </section>
        </>
      )}

      {tab === "recruiter" && (
        <section className="page-section recruiter-page">
          <div className="section-heading"><div><span className="section-kicker">RECRUITER MODE</span><h2>Candidate snapshot</h2><p className="tool-intro">A compact evidence-first view of the portfolio.</p></div></div>
          <div className="recruiter-grid">
            <article className="recruiter-profile-card"><img src="/profile.jpg" alt="Alok Agarwal" /><div><span className="section-kicker">CANDIDATE</span><h3>{candidate?.name || "Alok Agarwal"}</h3><p>{candidate?.headline || "Data Scientist & Python Developer"}</p><p className="muted">{candidate?.summary}</p></div></article>
            <div className="recruiter-actions">
              <button className="primary" onClick={() => setTab("jd")}><Search size={17} /> Analyze a JD</button>
              <button className="secondary" onClick={() => setTab("chat")}><MessageSquare size={17} /> Ask the AI</button>
              <a className="secondary" href="https://github.com/mightyalok00" target="_blank" rel="noreferrer"><Github size={17} /> GitHub profile</a>
            </div>
          </div>
          <div className="evidence-strip"><div><strong>{projectCount}</strong><span>documented projects</span></div><div><strong>{skillCount}</strong><span>documented skills</span></div><div><strong>{candidate?.education?.length || 0}</strong><span>verified education records</span></div><div><strong>{candidate?.experience?.length || 0}</strong><span>documented experience records</span></div></div>
          <div className="evidence-section"><div className="section-heading"><div><span className="section-kicker">SKILL EVIDENCE</span><h2>Skills connected to portfolio work</h2></div></div><div className="skill-evidence-grid">{skills.map((skill) => {
            const evidence = projects.filter((p) => (p.technologies || []).some((t) => t.toLowerCase() === skill.toLowerCase()));
            return (
              <button className="skill-evidence skill-evidence-button" key={skill} type="button" onClick={() => openSkillEvidence(skill)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openSkillEvidence(skill); } }}>
                <strong>{skill}</strong>
                <span>{evidence.length ? `${evidence.length} project${evidence.length === 1 ? "" : "s"}` : "Documented skill"}</span>
                {evidence.length > 0 && <small>{evidence.slice(0, 2).map((p) => p.name).join(" • ")}</small>}
                <em>{evidence.length ? "View supporting evidence →" : "View documentation →"}</em>
              </button>
            );
          })}</div></div>
        </section>
      )}

      {tab === "projects" && <section className="page-section"><div className="section-heading"><div><span className="section-kicker">PROJECT EXPLORER</span><h2>Portfolio projects</h2><p className="tool-intro">Open a project for its documented evidence and source links.</p></div></div><div className="project-grid">{projects.map((project) => <ProjectCard key={project.name} project={project} onOpen={setSelectedProject} />)}</div></section>}

      {tab === "chat" && (
        <section className="chat-workspace">
          <div className="chat-card">
            <div className="chat-header">
              <div>
                <strong>Recruiter Assistant</strong>
                <span>Evidence-grounded • Local Ollama • No hiring decision</span>
                {jdContext && <small className="chat-context-badge">JD context active • {jdContext.result.relevant_projects?.length || 0} relevant projects</small>}
              </div>
              <button className="icon-button" type="button" onClick={clearChat} title="Clear conversation"><Trash2 size={17} /></button>
            </div>

            <div className="chat-purpose">
              <div>
                <span className="section-kicker">RECRUITER COPILOT</span>
                <strong>Ask for evidence, not assumptions.</strong>
              </div>
              <span>Use the prompts below to scan the portfolio quickly.</span>
            </div>

            <div className="quick-row">
              {QUICK.map((question) => (
                <button type="button" key={question} onClick={() => sendMessage(question)} disabled={loading}>{question}</button>
              ))}
            </div>

            <div className="messages">
              {messages.map((message, index) => (
                <article key={index} className={`message ${message.role}`}>
                  <div className="message-label">{message.role === "assistant" ? "ALOK AI" : "RECRUITER"}</div>
                  <div className="message-body">{message.role === "assistant" ? <ReactMarkdown>{message.content || "Thinking…"}</ReactMarkdown> : message.content}</div>
                </article>
              ))}
              <div ref={bottom} />
            </div>

            <form className="composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
              <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about a project, technology, or documented experience..." disabled={loading} />
              <button type="submit" disabled={loading || !input.trim()}><Send size={17} /> {loading ? "Thinking…" : "Send"}</button>
            </form>
          </div>

          <aside className="chat-side-panel">
            <div className="chat-side-card">
              <span className="section-kicker">RECRUITER PROMPTS</span>
              <h3>Start with a focused question</h3>
              <div className="prompt-list">
                {RECRUITER_PROMPTS.map(([label, prompt]) => (
                  <button type="button" key={label} onClick={() => sendMessage(prompt)} disabled={loading}>
                    <strong>{label}</strong>
                    <span>{prompt}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="chat-side-card">
              <span className="section-kicker">PORTFOLIO CONTEXT</span>
              <h3>What the AI can verify</h3>
              <div className="context-stats">
                <div><strong>{projectCount}</strong><span>projects</span></div>
                <div><strong>{skillCount}</strong><span>skills</span></div>
              </div>
              <ul className="grounding-list">
                <li>Uses candidate profile and project evidence.</li>
                <li>Retrieves relevant portfolio documents when available.</li>
                <li>Does not treat missing education or employment as verified.</li>
                <li>Cannot make a hiring decision from the portfolio.</li>
              </ul>
              <div className="model-status">
                <span>LOCAL MODEL ROUTING</span>
                <strong>{apiHealth?.ollama_status === "connected" ? "Ollama connected" : apiHealth?.ollama_status || "Checking connection…"}</strong>
                <small>{apiHealth?.models?.general || "General model loading"}</small>
              </div>
            </div>
          </aside>
        </section>
      )}

      {tab === "jd" && (
        <section className="page-section tool-page">
          <div className="section-heading">
            <div><span className="section-kicker">RECRUITER TOOL</span><h2>Job Description Analyzer</h2></div>
          </div>
          <p className="tool-intro">Paste a JD to compare its requirements with documented portfolio evidence. The analyzer surfaces evidence; it does not make a hiring decision.</p>
          <div className="jd-input-card">
            <textarea className="jd-box" value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the job description here..." />
            <div className="jd-input-footer">
              <span>{jd.length} characters</span>
              <button className="primary" onClick={analyzeJD} disabled={loading || jd.length < 20}><Search size={17} /> {loading ? "Analyzing..." : "Analyze evidence"}</button>
            </div>
          </div>
          {jdResult && (
            <>
              <div className="jd-metrics">
                <JdMetric value={jdResult.matched_documented_skills?.length || 0} label="Documented matches" icon={CheckCircle2} />
                <JdMetric value={jdResult.relevant_projects?.length || 0} label="Relevant projects" icon={FolderKanban} />
                <JdMetric value={jdResult.requested_but_not_verified?.length || 0} label="Not verified" icon={AlertTriangle} />
                <JdMetric value={(jdResult.evidence || []).length} label="Evidence items" icon={Search} />
              </div>

              <div className="jd-results-grid">
                <ResultBlock title="Matched requirements" items={jdResult.matched_documented_skills} icon={CheckCircle2} tone="match" compact />
                <section className="result-block result-block-projects">
                  <div className="result-title"><FolderKanban size={16} /><h3>Relevant projects</h3><span>{jdResult.relevant_projects?.length || 0}</span></div>
                  {jdResult.relevant_projects?.length ? (
                    <div className="jd-project-list">
                      {jdResult.relevant_projects.map((name) => {
                        const project = projects.find((item) => item.name === name);
                        const matchedSkills = project
                          ? (project.technologies || []).filter((tech) =>
                              (jdResult.matched_documented_skills || []).some(
                                (skill) => skill.toLowerCase() === tech.toLowerCase()
                              )
                            ).slice(0, 5)
                          : [];
                        return (
                          <button className="jd-project-row" key={name} onClick={() => project && setSelectedProject(project)} disabled={!project}>
                            <span className="jd-project-copy">
                              <strong>{name}</strong>
                              {matchedSkills.length ? (
                                <span className="jd-project-tags">
                                  {matchedSkills.map((skill) => <em key={skill}>{skill}</em>)}
                                </span>
                              ) : (
                                <small>{project ? "Open documented project evidence" : "Project referenced by analyzer"}</small>
                              )}
                            </span>
                            <span className="jd-project-arrow">→</span>
                          </button>
                        );
                      })}
                    </div>
                  ) : <p className="empty-result">No relevant projects returned.</p>}
                </section>
              </div>

              <ResultBlock title="Requested but not verified" items={jdResult.requested_but_not_verified} icon={AlertTriangle} tone="warning" />

              <section className="evidence-panel">
                <div className="evidence-panel-head">
                  <div><span className="section-kicker">TRACEABLE EVIDENCE</span><h3>Evidence & notes</h3></div>
                  <div className="evidence-panel-actions">
                    <span>{(jdResult.evidence || []).length + (jdResult.notes || []).length} items</span>
                    <button
                      className="secondary jd-chat-button"
                      type="button"
                      onClick={() => {
                        setJdContext({ job_description: jd, result: jdResult });
                        setTab("chat");
                        setMessages((items) => [
                          ...items,
                          {
                            role: "assistant",
                            content: "JD context loaded. I can now answer follow-up questions using this analysis, the documented portfolio evidence, and the explicitly unverified requirements."
                          }
                        ]);
                      }}
                    >
                      <MessageSquare size={15} /> Discuss with AI
                    </button>
                  </div>
                </div>
                <div className="evidence-list">
                  {[...(jdResult.evidence || []), ...(jdResult.notes || [])].map((item, i) => <div className="evidence-line" key={`${item}-${i}`}><span>•</span><p>{item}</p></div>)}
                </div>
              </section>
            </>
          )}
        </section>
      )}

      {tab === "interview" && (
        <section className="page-section tool-page"><div className="section-heading"><div><span className="section-kicker">INTERVIEW MODE</span><h2>Practice from your portfolio</h2></div></div><div className="focus-row">{["machine learning", "Python", "SQL", "GenAI", "FastAPI"].map((item) => <button key={item} className={focus === item ? "selected" : ""} onClick={() => setFocus(item)}>{item}</button>)}</div><button className="primary" onClick={() => startInterview()} disabled={loading}><UserRound size={17} /> Generate question</button>{interview && <div className="interview-card"><span className="section-kicker">QUESTION</span><h3>{interview.question}</h3><p><strong>Why it matters:</strong> {interview.why_it_matters}</p><textarea className="answer-box" value={interviewAnswer} onChange={(e) => setInterviewAnswer(e.target.value)} placeholder="Write your answer here..." /><button className="secondary" onClick={() => startInterview(interviewAnswer)} disabled={loading || !interviewAnswer.trim()}>Evaluate & generate follow-up</button>{interview.evaluation && <div className="evaluation"><strong>Coaching:</strong><p>{interview.evaluation}</p><strong>Follow-up:</strong><p>{interview.follow_up}</p></div>}</div>}</section>
      )}

      {selectedSkill && <div className="modal-backdrop" onClick={() => setSelectedSkill(null)}>
        <article className="project-modal skill-modal" onClick={(event) => event.stopPropagation()}>
          <button className="modal-close" onClick={() => setSelectedSkill(null)}><X size={18} /></button>
          <span className="section-kicker">SKILL EVIDENCE</span>
          <h2>{selectedSkill.name}</h2>
          <p className="modal-description">
            {selectedSkill.projects.length
              ? `Documented across ${selectedSkill.projects.length} portfolio project${selectedSkill.projects.length === 1 ? "" : "s"}.`
              : "The skill is documented in the candidate profile, but no project-level technology evidence is currently recorded."}
          </p>
          {selectedSkill.projects.length ? (
            <div className="skill-project-list">
              {selectedSkill.projects.map((project) => (
                <button type="button" className="skill-project-row" key={project.name} onClick={() => { setSelectedSkill(null); setSelectedProject(project); }}>
                  <span>
                    <strong>{project.name}</strong>
                    <small>{(project.technologies || []).filter((tech) => tech.toLowerCase() === selectedSkill.name.toLowerCase()).join(" • ") || "Documented project evidence"}</small>
                  </span>
                  <span>View project →</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="evidence-note"><strong>Documentation note</strong><p>No project-level evidence is currently recorded for this skill.</p></div>
          )}
        </article>
      </div>}

      {selectedProject && <div className="modal-backdrop" onClick={() => setSelectedProject(null)}><article className="project-modal" onClick={(event) => event.stopPropagation()}><button className="modal-close" onClick={() => setSelectedProject(null)}><X size={18} /></button><span className="section-kicker">PROJECT DETAIL</span><h2>{selectedProject.name}</h2><p className="modal-description">{selectedProject.description}</p><div className="chips">{(selectedProject.technologies || []).map((tech) => <span key={tech}>{tech}</span>)}</div><div className="evidence-note"><strong>Documented evidence</strong><ul>{(selectedProject.evidence_notes || []).map((note) => <li key={note}>{note}</li>)}</ul></div><div className="modal-actions">{selectedProject.repository && <a className="primary" href={selectedProject.repository} target="_blank" rel="noreferrer"><Github size={17} /> View GitHub</a>}{selectedProject.demo && <a className="secondary" href={selectedProject.demo} target="_blank" rel="noreferrer"><ExternalLink size={17} /> Live demo</a>}<button className="secondary" onClick={() => { setSelectedProject(null); setTab("chat"); setTimeout(() => sendMessage(`Explain the documented evidence for the ${selectedProject.name} project.`), 0); }}><MessageSquare size={17} /> Ask AI</button></div></article></div>}

      <footer>Alok AI • React + FastAPI + Ollama • Evidence-grounded local AI</footer>
    </main>
  );
}
