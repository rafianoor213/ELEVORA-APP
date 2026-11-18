import { useEffect, useMemo, useState } from 'react';

import {
  Activity,
  ArrowRight,
  Award,
  BookOpen,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Code2,
  Compass,
  FileText,
  GraduationCap,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  MessageSquare,
  Rocket,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Trophy,
  UserRound,
  X,
  Zap,
} from 'lucide-react';


async function postAI(payload: Record<string, unknown>) {
  const response = await fetch('/api/ai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`AI service returned ${response.status}`);
  return { data: await response.json() };
}

type Profile = {
  name: string;
  email: string;
  education: string;
  targetRole: string;
  skills: string[];
  hours: number;
};
type Project = {
  title: string;
  description: string;
  url: string;
  github: string;
  feedback: string;
  score: number;
  submitted: boolean;
};
const initialProfile: Profile = {
  name: 'Alex Morgan',
  email: 'alex@example.com',
  education: 'University student',
  targetRole: 'Frontend Developer',
  skills: ['HTML', 'CSS'],
  hours: 6,
};
const requiredSkills = [
  'HTML',
  'CSS',
  'JavaScript',
  'Responsive Design',
  'Git & GitHub',
  'React',
  'API Integration',
];
const lessons = [
  {
    id: 'js',
    stage: '01',
    skill: 'JavaScript fundamentals',
    detail: 'Variables, functions, arrays, DOM and events',
    time: '8 hours',
    resource: 'https://javascript.info/',
  },
  {
    id: 'responsive',
    stage: '02',
    skill: 'Responsive design',
    detail: 'Build layouts that work across screen sizes',
    time: '4 hours',
    resource:
      'https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design',
  },
  {
    id: 'git',
    stage: '03',
    skill: 'Git & GitHub',
    detail: 'Version control, commits, branches and repositories',
    time: '3 hours',
    resource: 'https://docs.github.com/en/get-started',
  },
  {
    id: 'react',
    stage: '04',
    skill: 'React fundamentals',
    detail: 'Components, props, state and hooks',
    time: '10 hours',
    resource: 'https://react.dev/learn',
  },
  {
    id: 'api',
    stage: '05',
    skill: 'API integration',
    detail: 'Fetch data, handle loading and error states',
    time: '4 hours',
    resource: 'https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API',
  },
];
const jobs = [
  {
    title: 'Frontend Developer Intern',
    company: 'Northstar Labs',
    type: 'Internship',
    location: 'Remote · Sample listing',
    skills: ['HTML', 'CSS', 'JavaScript', 'Responsive Design'],
    level: 'Entry level',
  },
  {
    title: 'Junior Web Developer',
    company: 'Pixel & Code',
    type: 'Full-time',
    location: 'Dhaka · Sample listing',
    skills: ['HTML', 'CSS', 'JavaScript', 'Git & GitHub', 'React'],
    level: '0–1 years',
  },
  {
    title: 'React Developer Intern',
    company: 'Launchpad Studio',
    type: 'Internship',
    location: 'Hybrid · Sample listing',
    skills: ['JavaScript', 'React', 'API Integration', 'Git & GitHub'],
    level: 'Entry level',
  },
];
const nav = [
  {
    group: 'WORKSPACE',
    items: [
      { id: 'Overview', icon: LayoutDashboard },
      { id: 'Career Advisor', icon: Compass },
      { id: 'Job Market', icon: BriefcaseBusiness },
      { id: 'Skill Gap', icon: Activity },
    ],
  },
  {
    group: 'YOUR JOURNEY',
    items: [
      { id: 'Learning Roadmap', icon: BookOpen },
      { id: 'Projects', icon: Code2 },
      { id: 'My Portfolio', icon: Award },
      { id: 'Opportunities', icon: Rocket },
    ],
  },
];
function readSaved<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}
function App() {
  const [page, setPage] = useState('Overview');
  const [profile, setProfile] = useState<Profile>(() =>
    readSaved('elevora-profile', initialProfile)
  );
  const [completed, setCompleted] = useState<string[]>(() =>
    readSaved('elevora-completed', [])
  );
  const [project, setProject] = useState<Project>(() =>
    readSaved('elevora-project', {
      title: 'Interactive Task Manager',
      description: '',
      url: '',
      github: '',
      feedback: '',
      score: 0,
      submitted: false,
    })
  );
  const [onboarding, setOnboarding] = useState(
    () => !localStorage.getItem('elevora-onboarded')
  );
  const [draft, setDraft] = useState<Profile>(profile);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [aiBusy, setAiBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [projectBusy, setProjectBusy] = useState(false);
  useEffect(() => {
    localStorage.setItem('elevora-profile', JSON.stringify(profile));
  }, [profile]);
  useEffect(() => {
    localStorage.setItem('elevora-completed', JSON.stringify(completed));
  }, [completed]);
  useEffect(() => {
    localStorage.setItem('elevora-project', JSON.stringify(project));
  }, [project]);
  const missing = useMemo(
    () =>
      requiredSkills.filter(
        s =>
          !profile.skills.includes(s) &&
          !(s === 'JavaScript' && completed.includes('js')) &&
          !(s === 'Responsive Design' && completed.includes('responsive')) &&
          !(s === 'Git & GitHub' && completed.includes('git')) &&
          !(s === 'React' && completed.includes('react')) &&
          !(s === 'API Integration' && completed.includes('api'))
      ),
    [profile.skills, completed]
  );
  const skillScore = Math.round(
    ((requiredSkills.length - missing.length) / requiredSkills.length) * 100
  );
  const progress = Math.round((completed.length / lessons.length) * 100);
  const notify = (message: string) => {
    setNotice(message);
    window.setTimeout(() => setNotice(''), 2800);
  };
  const toggleLesson = (id: string) =>
    setCompleted(old =>
      old.includes(id) ? old.filter(x => x !== id) : [...old, id]
    );
  const askAI = async (mode: 'advisor' | 'project') => {
    const prompt =
      mode === 'advisor'
        ? question
        : `Review this Frontend Developer learning project submission. Project description: ${project.description}. Live URL: ${project.url || 'Not provided'}. GitHub URL: ${project.github || 'Not provided'}. Give a transparent rubric-based review, strengths, improvements, and next steps. Do not claim to have opened links or inspected code.`;
    if (!prompt.trim()) {
      notify('Please add some details first.');
      return;
    }
    setAiBusy(true);
    try {
      const result = await postAI({
        mode,
        prompt,
        profile: {
          targetRole: profile.targetRole,
          skills: profile.skills,
          completed,
        },
      });
      setAnswer(
        result.data.text ||
          'Your request was processed, but no text was returned.'
      );
    } catch {
      setAnswer(
        mode === 'advisor'
          ? 'Based on your Frontend Developer goal, prioritize JavaScript fundamentals, responsive layouts, and Git. Build a small interactive project after each topic. Your next best step is to complete the JavaScript roadmap module, then revisit your skill profile.'
          : 'Sample rubric feedback (rule-based fallback): Your submission is ready for a manual review. Check semantic HTML, responsive behavior, JavaScript interactions, code organization, and accessibility. Add a clear README and screenshots to strengthen your portfolio. This fallback has not inspected your submitted links.'
      );
    } finally {
      setAiBusy(false);
    }
  };
  const submitProject = async () => {
    if (!project.description.trim()) {
      notify('Add a short project description before submitting.');
      return;
    }
    setProjectBusy(true);
    setAnswer('');
    try {
      const result = await postAI({
        mode: 'project',
        prompt: `Review this Frontend Developer learning project submission. Project description: ${project.description}. Live URL: ${project.url || 'Not provided'}. GitHub URL: ${project.github || 'Not provided'}. Give a transparent rubric-based review, strengths, improvements, and next steps. Do not claim to have opened links or inspected code.`,
        profile: {
          targetRole: profile.targetRole,
          skills: profile.skills,
          completed,
        },
      });
      const feedback = result.data.text || 'No feedback text was returned.';
      setProject(p => ({ ...p, feedback, score: 78, submitted: true }));
      notify('Project submitted. Feedback is ready.');
    } catch {
      const feedback =
        'Sample rubric feedback (rule-based fallback): Your submission is ready for a manual review. Check semantic HTML, responsive behavior, JavaScript interactions, code organization, and accessibility. Add a clear README and screenshots to strengthen your portfolio. This fallback has not inspected your submitted links.';
      setProject(p => ({ ...p, feedback, score: 72, submitted: true }));
      notify('Project saved with sample feedback.');
    } finally {
      setProjectBusy(false);
    }
  };
  const finishOnboarding = () => {
    if (!draft.name.trim()) return;
    setProfile(draft);
    localStorage.setItem('elevora-onboarded', 'yes');
    setOnboarding(false);
    notify('Your career workspace is ready.');
  };
  const match = (skills: string[]) =>
    Math.round(
      (skills.filter(
        s =>
          profile.skills.includes(s) ||
          completed.some(id =>
            lessons
              .find(l => l.id === id)
              ?.skill.toLowerCase()
              .includes(s.toLowerCase().split(' ')[0])
          )
      ).length /
        skills.length) *
        100
    );
  const go = (id: string) => {
    setPage(id);
    setMobileOpen(false);
    setAnswer('');
  };
  const pageTitle: Record<string, string> = {
    Overview: 'Your career overview',
    'Career Advisor': 'AI Career Advisor',
    'Job Market': 'Job Market Analyzer',
    'Skill Gap': 'Skill-Gap Analysis',
    'Learning Roadmap': 'Your learning roadmap',
    Projects: 'Practical projects',
    'My Portfolio': 'Your skill portfolio',
    Opportunities: 'Matched opportunities',
  };

  if (onboarding)
    return (
      <div className="onboard-shell">
        <div className="onboard-card">
          <div className="brand">
            <span className="brand-mark">
              <Sparkles size={19} />
            </span>
            <span>
              ELEVORA<span className="brand-ai"> AI</span>
            </span>
          </div>
          <div className="eyebrow">YOUR CAREER JOURNEY STARTS HERE</div>
          <h1>Let's build your next chapter.</h1>
          <p className="muted">
            Tell us a little about yourself. We'll shape your workspace around
            your career goal.
          </p>
          <div className="form-grid">
            <label>
              YOUR NAME
              <input
                value={draft.name}
                onChange={e => setDraft({ ...draft, name: e.target.value })}
                placeholder="e.g. Alex Morgan"
              />
            </label>
            <label>
              EMAIL ADDRESS
              <input
                type="email"
                value={draft.email}
                onChange={e => setDraft({ ...draft, email: e.target.value })}
                placeholder="you@example.com"
              />
            </label>
            <label>
              YOUR CURRENT STATUS
              <select
                value={draft.education}
                onChange={e =>
                  setDraft({ ...draft, education: e.target.value })
                }
              >
                <option>University student</option>
                <option>Fresh graduate</option>
                <option>Entry-level job seeker</option>
                <option>Career changer</option>
              </select>
            </label>
            <label>
              TARGET CAREER
              <select
                value={draft.targetRole}
                onChange={e =>
                  setDraft({ ...draft, targetRole: e.target.value })
                }
              >
                <option>Frontend Developer</option>
                <option>UI/UX Designer</option>
                <option>Backend Developer</option>
              </select>
            </label>
          </div>
          <div className="field-label">SKILLS YOU ALREADY HAVE</div>
          <div className="skill-picks">
            {[
              'HTML',
              'CSS',
              'JavaScript',
              'Responsive Design',
              'Git & GitHub',
              'React',
            ].map(s => (
              <button
                key={s}
                className={
                  draft.skills.includes(s)
                    ? 'skill-pick selected'
                    : 'skill-pick'
                }
                onClick={() =>
                  setDraft({
                    ...draft,
                    skills: draft.skills.includes(s)
                      ? draft.skills.filter(x => x !== s)
                      : [...draft.skills, s],
                  })
                }
              >
                {draft.skills.includes(s) ? (
                  <Check size={14} />
                ) : (
                  <span className="pick-dot" />
                )}
                {s}
              </button>
            ))}
          </div>
          <label className="hours-label">
            WEEKLY LEARNING TIME{' '}
            <select
              value={draft.hours}
              onChange={e =>
                setDraft({ ...draft, hours: Number(e.target.value) })
              }
            >
              <option value={3}>3 hours</option>
              <option value={6}>6 hours</option>
              <option value={10}>10 hours</option>
              <option value={15}>15+ hours</option>
            </select>
          </label>
          <button
            className="btn btn-primary btn-wide"
            onClick={finishOnboarding}
          >
            Create my career roadmap <ArrowRight size={17} />
          </button>
          <p className="tiny center">
            Demo workspace · Your progress is saved in this browser
          </p>
        </div>
      </div>
    );

  return (
    <div className="app-shell">
      <aside className={mobileOpen ? 'sidebar mobile-visible' : 'sidebar'}>
        <div className="sidebar-top">
          <div className="brand">
            <span className="brand-mark">
              <Sparkles size={19} />
            </span>
            <span>
              ELEVORA<span className="brand-ai"> AI</span>
            </span>
          </div>
          <button
            className="icon-btn close-mobile"
            onClick={() => setMobileOpen(false)}
          >
            <X />
          </button>
        </div>
        <div className="workspace-label">PERSONAL WORKSPACE</div>
        {nav.map(group => (
          <div className="nav-group" key={group.group}>
            <div className="nav-caption">{group.group}</div>
            {group.items.map(item => (
              <button
                key={item.id}
                className={page === item.id ? 'nav-item active' : 'nav-item'}
                onClick={() => go(item.id)}
              >
                <item.icon size={17} />
                <span>{item.id}</span>
                {item.id === 'Opportunities' && (
                  <span className="nav-count">3</span>
                )}
              </button>
            ))}
          </div>
        ))}
        <div className="sidebar-bottom">
          <div className="sidebar-help">
            <div className="help-icon">
              <Lightbulb size={17} />
            </div>
            <div>
              <b>Keep moving forward</b>
              <span>Small steps build big careers.</span>
            </div>
          </div>
          <button className="profile-mini" onClick={() => go('My Portfolio')}>
            <div className="avatar">
              {profile.name.slice(0, 1).toUpperCase()}
            </div>
            <div className="profile-mini-text">
              <b>{profile.name}</b>
              <span>{profile.targetRole}</span>
            </div>
            <ChevronDown size={15} />
          </button>
        </div>
      </aside>
      {mobileOpen && (
        <div className="mobile-scrim" onClick={() => setMobileOpen(false)} />
      )}
      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-btn menu-btn"
            onClick={() => setMobileOpen(true)}
          >
            <Menu />
          </button>
          <div className="crumb">
            Workspace <span>/</span> <b>{page}</b>
          </div>
          <div className="top-actions">
            <span className="demo-pill">
              <span /> DEMO MODE
            </span>
            <button
              className="icon-btn"
              title="Help"
              onClick={() =>
                notify('Your progress is saved automatically in this browser.')
              }
            >
              <CircleHelp size={18} />
            </button>
            <div className="avatar small">
              {profile.name.slice(0, 1).toUpperCase()}
            </div>
          </div>
        </header>
        <div className="content-wrap">
          <div className="page-heading">
            <div>
              <div className="eyebrow">WEDNESDAY, NOVEMBER 18, 2026</div>
              <h1>{pageTitle[page]}</h1>
              <p>
                {page === 'Overview'
                  ? 'A clear path from what you know to what comes next.'
                  : page === 'Career Advisor'
                    ? 'Get practical guidance for the career you want.'
                    : 'Build skills with purpose. Make every next step count.'}
              </p>
            </div>
            <button
              className="btn btn-soft"
              onClick={() => {
                setDraft(profile);
                setOnboarding(true);
              }}
            >
              <Settings size={16} /> Edit profile
            </button>
          </div>
          {page === 'Overview' && (
            <>
              <section className="welcome-banner">
                <div className="welcome-copy">
                  <div className="welcome-kicker">
                    <Sparkles size={14} /> YOUR PERSONAL CAREER COMPANION
                  </div>
                  <h2>
                    You're closer than
                    <br />
                    you think, {profile.name.split(' ')[0]}.
                  </h2>
                  <p>
                    Your goal is <b>{profile.targetRole}</b>. Let's turn your
                    current skills into real opportunities, one step at a time.
                  </p>
                  <button
                    className="btn btn-white"
                    onClick={() => go('Skill Gap')}
                  >
                    View my skill gaps <ArrowRight size={16} />
                  </button>
                </div>
                <div className="banner-art">
                  <div className="orbit orbit-one" />
                  <div className="orbit orbit-two" />
                  <div className="orbit-core">
                    <Rocket size={44} />
                  </div>
                  <div className="float-chip chip-a">
                    <CheckCircle2 size={15} /> Career path mapped
                  </div>
                  <div className="float-chip chip-b">
                    <Zap size={15} /> Skills in progress
                  </div>
                </div>
              </section>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Career skill match</span>
                    <Target size={17} />
                  </div>
                  <div className="stat-value">{skillScore}%</div>
                  <div className="stat-foot">
                    <span className="positive">
                      <TrendingUp size={13} /> Based on 7 core skills
                    </span>
                  </div>
                  <div className="mini-track">
                    <i style={{ width: skillScore + '%' }} />
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Learning progress</span>
                    <BookOpen size={17} />
                  </div>
                  <div className="stat-value">{progress}%</div>
                  <div className="stat-foot">
                    {completed.length} of {lessons.length} modules completed
                  </div>
                  <div className="mini-track purple">
                    <i style={{ width: progress + '%' }} />
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Projects submitted</span>
                    <Code2 size={17} />
                  </div>
                  <div className="stat-value">
                    {project.submitted ? 1 : 0}
                    <small> / 1</small>
                  </div>
                  <div className="stat-foot">
                    {project.submitted
                      ? 'Your project is in your portfolio'
                      : 'Your first project is waiting'}
                  </div>
                  <div className="stat-icon">
                    <Award size={19} />
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Skills to strengthen</span>
                    <Activity size={17} />
                  </div>
                  <div className="stat-value">{missing.length}</div>
                  <div className="stat-foot">
                    Prioritized for your target role
                  </div>
                  <div className="stat-icon amber">
                    <Zap size={19} />
                  </div>
                </div>
              </div>
              <div className="section-row">
                <div>
                  <h3>Your Learn-to-Prove-to-Earn journey</h3>
                  <p className="muted">
                    Every stage builds on the one before it.
                  </p>
                </div>
                <span className="live-tag">
                  <span /> YOUR PATHWAY
                </span>
              </div>
              <div className="journey-grid">
                <button
                  className="journey-card"
                  onClick={() => go('Learning Roadmap')}
                >
                  <div className="journey-icon lavender">
                    <BookOpen />
                  </div>
                  <div className="journey-step">01 · LEARN</div>
                  <h3>Build the right skills</h3>
                  <p>Follow a roadmap shaped around real role requirements.</p>
                  <div className="journey-bottom">
                    <span>
                      {completed.length}/{lessons.length} lessons done
                    </span>
                    <ArrowRight size={17} />
                  </div>
                </button>
                <button className="journey-card" onClick={() => go('Projects')}>
                  <div className="journey-icon mint">
                    <Code2 />
                  </div>
                  <div className="journey-step">02 · PROVE</div>
                  <h3>Show what you can do</h3>
                  <p>Turn your learning into practical project evidence.</p>
                  <div className="journey-bottom">
                    <span>
                      {project.submitted
                        ? 'Project submitted'
                        : '1 project assigned'}
                    </span>
                    <ArrowRight size={17} />
                  </div>
                </button>
                <button
                  className="journey-card"
                  onClick={() => go('Opportunities')}
                >
                  <div className="journey-icon peach">
                    <Rocket />
                  </div>
                  <div className="journey-step">03 · EARN</div>
                  <h3>Find your next opportunity</h3>
                  <p>
                    Explore sample roles aligned with your demonstrated skills.
                  </p>
                  <div className="journey-bottom">
                    <span>3 curated opportunities</span>
                    <ArrowRight size={17} />
                  </div>
                </button>
              </div>
              <div className="two-col">
                <section className="panel">
                  <div className="panel-head">
                    <div>
                      <h3>Recommended next steps</h3>
                      <p className="muted">A little progress, consistently.</p>
                    </div>
                    <button
                      className="text-link"
                      onClick={() => go('Learning Roadmap')}
                    >
                      View roadmap <ArrowRight size={14} />
                    </button>
                  </div>
                  {missing.slice(0, 3).map((s, i) => (
                    <div className="next-step" key={s}>
                      <div className="step-number">0{i + 1}</div>
                      <div className="step-text">
                        <b>{s}</b>
                        <span>
                          {i === 0
                            ? 'High priority · Core skill'
                            : i === 1
                              ? 'Build confidence through practice'
                              : 'Strengthen your toolkit'}
                        </span>
                      </div>
                      <button
                        className="round-arrow"
                        onClick={() => go('Learning Roadmap')}
                      >
                        <ArrowRight size={15} />
                      </button>
                    </div>
                  ))}
                  {missing.length === 0 && (
                    <p className="muted">
                      You've covered all listed core skills. Build another
                      project to strengthen your evidence.
                    </p>
                  )}
                </section>
                <section className="panel">
                  <div className="panel-head">
                    <div>
                      <h3>Opportunity preview</h3>
                      <p className="muted">Curated sample listings</p>
                    </div>
                    <button
                      className="text-link"
                      onClick={() => go('Opportunities')}
                    >
                      See all <ArrowRight size={14} />
                    </button>
                  </div>
                  {jobs.slice(0, 2).map(j => (
                    <div className="job-preview" key={j.title}>
                      <div className="company-mark">
                        {j.company.slice(0, 1)}
                      </div>
                      <div className="job-info">
                        <b>{j.title}</b>
                        <span>
                          {j.company} · {j.type}
                        </span>
                      </div>
                      <span className="match-badge">
                        {match(j.skills)}% match
                      </span>
                    </div>
                  ))}
                  <div className="sample-note">
                    <ShieldCheck size={14} /> Sample opportunities · Not live
                    vacancies
                  </div>
                </section>
              </div>
            </>
          )}
          {page === 'Career Advisor' && (
            <div className="feature-layout">
              <section className="panel advisor-panel">
                <div className="feature-icon">
                  <Sparkles />
                </div>
                <div className="eyebrow">ELEVORA AI CAREER COACH</div>
                <h2>Let's make your next move clearer.</h2>
                <p className="muted">
                  Ask about your career direction, skills to prioritize, or how
                  to prepare for a Frontend Developer role. Responses are
                  guidance, not a hiring decision.
                </p>
                <div className="suggestion-row">
                  {[
                    'What should I learn next?',
                    'How do I build a strong portfolio?',
                    'Am I ready for an internship?',
                  ].map(q => (
                    <button onClick={() => setQuestion(q)}>{q}</button>
                  ))}
                </div>
                <textarea
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  placeholder="Tell me what you're working toward..."
                  rows={4}
                />
                <button
                  className="btn btn-primary"
                  disabled={aiBusy}
                  onClick={() => askAI('advisor')}
                >
                  {aiBusy ? 'Thinking...' : 'Ask Elevora AI'} <Send size={16} />
                </button>
                {answer && (
                  <div className="ai-response">
                    <div className="response-head">
                      <Sparkles size={16} /> ELEVORA'S GUIDANCE{' '}
                      <span>AI / fallback</span>
                    </div>
                    <p>{answer}</p>
                  </div>
                )}
              </section>
              <aside className="panel coach-side">
                <h3>Your career snapshot</h3>
                <div className="snapshot-role">
                  <div className="journey-icon lavender">
                    <Code2 />
                  </div>
                  <div>
                    <b>{profile.targetRole}</b>
                    <span>Current target role</span>
                  </div>
                </div>
                <div className="snapshot-row">
                  <span>Skill match</span>
                  <b>{skillScore}%</b>
                </div>
                <div className="mini-track">
                  <i style={{ width: skillScore + '%' }} />
                </div>
                <div className="snapshot-row">
                  <span>Skills to strengthen</span>
                  <b>{missing.length}</b>
                </div>
                <div className="divider-line" />
                <h4>Suggested focus areas</h4>
                {missing.slice(0, 4).map(s => (
                  <div className="focus-pill">
                    <Target size={13} />
                    {s}
                  </div>
                ))}
              </aside>
            </div>
          )}
          {page === 'Job Market' && (
            <>
              <div className="market-intro">
                <div>
                  <h2>What are employers looking for?</h2>
                  <p className="muted">
                    A small curated dataset to help you understand the skills
                    behind entry-level frontend roles.
                  </p>
                </div>
                <span className="sample-tag">CURATED SAMPLE DATA</span>
              </div>
              <div className="market-grid">
                <section className="panel">
                  <h3>Frequently requested skills</h3>
                  <p className="muted">
                    Illustrative frequency across our sample listings.
                  </p>
                  {requiredSkills.map((s, i) => (
                    <div className="market-skill">
                      <span>{s}</span>
                      <div className="market-bar">
                        <i
                          style={{
                            width: [95, 90, 82, 70, 58, 52, 42][i] + '%',
                          }}
                        />
                      </div>
                      <b>{[3, 3, 3, 2, 2, 2, 1][i]}/3</b>
                    </div>
                  ))}
                </section>
                <section className="panel">
                  <h3>What this means for you</h3>
                  <p className="muted">
                    Compare employer requirements with your current profile.
                  </p>
                  <div className="insight-number">
                    {missing.length}
                    <span> skills to strengthen</span>
                  </div>
                  <p className="muted">
                    Focus first on JavaScript and responsive design, then build
                    toward React and API integration.
                  </p>
                  <button
                    className="btn btn-primary"
                    onClick={() => go('Skill Gap')}
                  >
                    Analyze my skill gaps <ArrowRight size={15} />
                  </button>
                </section>
              </div>
              <div className="section-row">
                <div>
                  <h3>Sample role descriptions</h3>
                  <p className="muted">
                    These listings are illustrative, not active vacancies.
                  </p>
                </div>
              </div>
              <div className="job-list">
                {jobs.map(j => (
                  <div className="panel job-row">
                    <div className="company-mark">{j.company.slice(0, 1)}</div>
                    <div className="job-main">
                      <b>{j.title}</b>
                      <span>
                        {j.company} · {j.type} · {j.level}
                      </span>
                      <div className="tag-row">
                        {j.skills.map(s => (
                          <span>{s}</span>
                        ))}
                      </div>
                    </div>
                    <span className="match-badge">
                      {match(j.skills)}% match
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
          {page === 'Skill Gap' && (
            <>
              <div className="skill-summary panel">
                <div>
                  <div className="eyebrow">
                    YOUR TARGET · {profile.targetRole.toUpperCase()}
                  </div>
                  <h2>
                    {skillScore}% <span>current skill match</span>
                  </h2>
                  <p className="muted">
                    Based on {requiredSkills.length} core skills in our curated
                    role profile. This is a skill overlap indicator, not a
                    job-readiness score.
                  </p>
                </div>
                <div
                  className="score-ring"
                  style={{ '--score': skillScore + '%' } as React.CSSProperties}
                >
                  <div>
                    <b>{skillScore}%</b>
                    <span>match</span>
                  </div>
                </div>
              </div>
              <div className="skill-columns">
                <section className="panel">
                  <div className="panel-head">
                    <h3>
                      <CheckCircle2 className="green-text" size={18} /> Skills
                      you have
                    </h3>
                    <span className="count-pill">
                      {requiredSkills.length - missing.length}
                    </span>
                  </div>
                  {requiredSkills
                    .filter(s => !missing.includes(s))
                    .map(s => (
                      <div className="skill-line">
                        <span>{s}</span>
                        <span className="status-have">
                          <Check size={14} /> In profile
                        </span>
                      </div>
                    ))}
                </section>
                <section className="panel">
                  <div className="panel-head">
                    <h3>
                      <Target className="purple-text" size={18} /> Skills to
                      strengthen
                    </h3>
                    <span className="count-pill purple-count">
                      {missing.length}
                    </span>
                  </div>
                  {missing.map((s, i) => (
                    <div className="skill-line">
                      <span>{s}</span>
                      <span className={i < 2 ? 'priority high' : 'priority'}>
                        {i < 2 ? 'High priority' : 'Next step'}
                      </span>
                    </div>
                  ))}
                </section>
              </div>
              <div className="panel gap-explainer">
                <h3>Why these skills matter</h3>
                <p className="muted">
                  JavaScript brings interactivity to web pages. Responsive
                  design makes products usable across devices. Git supports
                  collaboration, while React and API integration help you build
                  more complete applications.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => go('Learning Roadmap')}
                >
                  Build my learning plan <ArrowRight size={15} />
                </button>
              </div>
            </>
          )}
          {page === 'Learning Roadmap' && (
            <>
              <div className="roadmap-hero panel">
                <div>
                  <div className="eyebrow">
                    PERSONALIZED FOR {profile.targetRole.toUpperCase()}
                  </div>
                  <h2>Your next skill, your next milestone.</h2>
                  <p className="muted">
                    A focused path based on the skills you want to strengthen.
                  </p>
                </div>
                <div className="roadmap-progress">
                  <b>{progress}%</b>
                  <span>completed</span>
                  <div className="mini-track">
                    <i style={{ width: progress + '%' }} />
                  </div>
                </div>
              </div>
              <div className="roadmap-list">
                {lessons.map((l, i) => (
                  <div
                    className={
                      completed.includes(l.id)
                        ? 'roadmap-item done'
                        : 'roadmap-item'
                    }
                  >
                    <div className="roadmap-marker">
                      {completed.includes(l.id) ? <Check size={17} /> : l.stage}
                    </div>
                    <div className="roadmap-detail">
                      <div className="lesson-meta">
                        MODULE {l.stage} <span>·</span> {l.time}
                      </div>
                      <h3>{l.skill}</h3>
                      <p>{l.detail}</p>
                      <a href={l.resource} target="_blank" rel="noreferrer">
                        Open free learning resource <ArrowRight size={13} />
                      </a>
                    </div>
                    <button
                      className={
                        completed.includes(l.id)
                          ? 'btn btn-complete'
                          : 'btn btn-outline'
                      }
                      onClick={() => toggleLesson(l.id)}
                    >
                      {completed.includes(l.id) ? (
                        <>
                          <Check size={15} /> Completed
                        </>
                      ) : (
                        'Mark complete'
                      )}
                    </button>
                  </div>
                ))}
              </div>
              <div className="sample-note">
                <Lightbulb size={15} /> Learning resources link to external
                documentation. Completion is self-reported.
              </div>
            </>
          )}
          {page === 'Projects' && (
            <>
              <div className="project-hero">
                <div className="project-label">
                  <Code2 size={15} /> YOUR PROVE STAGE
                </div>
                <h2>Turn knowledge into something real.</h2>
                <p>
                  One practical project can make your learning visible. Build,
                  submit, and reflect.
                </p>
              </div>
              <div className="project-layout">
                <section className="panel project-brief">
                  <div className="brief-top">
                    <span className="sample-tag">BEGINNER · FRONTEND</span>
                    <span className="time-estimate">◷ 6–8 hours</span>
                  </div>
                  <h2>Interactive Task Manager</h2>
                  <p className="muted">
                    Build a responsive task management app where users can add,
                    complete, filter, and delete tasks.
                  </p>
                  <h4>What you'll practice</h4>
                  <div className="tag-row">
                    {[
                      'Semantic HTML',
                      'CSS layout',
                      'JavaScript DOM',
                      'Event handling',
                      'Responsive design',
                    ].map(s => (
                      <span>{s}</span>
                    ))}
                  </div>
                  <h4>Assessment rubric</h4>
                  {[
                    'HTML structure & semantics',
                    'Visual design & responsiveness',
                    'JavaScript functionality',
                    'User interactions',
                    'Code organization',
                  ].map((s, i) => (
                    <div className="rubric-row">
                      <span>{s}</span>
                      <b>{[20, 20, 25, 20, 15][i]} pts</b>
                    </div>
                  ))}
                </section>
                <section className="panel submit-panel">
                  <div className="panel-head">
                    <h3>Submit your work</h3>
                    <span className="status-draft">
                      {project.submitted ? 'Submitted' : 'In progress'}
                    </span>
                  </div>
                  <label>
                    PROJECT DESCRIPTION
                    <textarea
                      rows={4}
                      value={project.description}
                      onChange={e =>
                        setProject({
                          ...project,
                          description: e.target.value,
                          submitted: false,
                        })
                      }
                      placeholder="Describe what you built, which features work, and what you learned..."
                    />
                  </label>
                  <label>
                    LIVE PROJECT URL{' '}
                    <input
                      value={project.url}
                      onChange={e =>
                        setProject({
                          ...project,
                          url: e.target.value,
                          submitted: false,
                        })
                      }
                      placeholder="https://your-project.example"
                    />
                  </label>
                  <label>
                    GITHUB REPOSITORY URL{' '}
                    <input
                      value={project.github}
                      onChange={e =>
                        setProject({
                          ...project,
                          github: e.target.value,
                          submitted: false,
                        })
                      }
                      placeholder="https://github.com/username/project"
                    />
                  </label>
                  <button
                    className="btn btn-primary btn-wide"
                    disabled={projectBusy}
                    onClick={submitProject}
                  >
                    {projectBusy ? 'Reviewing...' : 'Submit for feedback'}{' '}
                    <ArrowRight size={16} />
                  </button>
                  <p className="tiny">
                    AI feedback is based on the information you provide. Links
                    are not automatically inspected.
                  </p>
                  {project.feedback && (
                    <div className="feedback-box">
                      <div className="response-head">
                        <Sparkles size={15} /> PROJECT FEEDBACK{' '}
                        <span>{project.score}/100 · sample rubric</span>
                      </div>
                      <p>{project.feedback}</p>
                    </div>
                  )}
                </section>
              </div>
            </>
          )}
          {page === 'My Portfolio' && (
            <>
              <div className="portfolio-hero panel">
                <div className="portfolio-avatar">
                  {profile.name.slice(0, 1).toUpperCase()}
                </div>
                <div>
                  <div className="eyebrow">LEARNER PROFILE</div>
                  <h2>{profile.name}</h2>
                  <p>
                    {profile.targetRole} · {profile.education}
                  </p>
                  <span className="profile-email">{profile.email}</span>
                </div>
                <button
                  className="btn btn-soft"
                  onClick={() =>
                    notify(
                      'Public portfolio publishing is planned for a future version.'
                    )
                  }
                >
                  Preview profile <ArrowRight size={14} />
                </button>
              </div>
              <div className="portfolio-grid">
                <section className="panel">
                  <h3>Skill profile</h3>
                  <p className="muted">
                    Self-reported and learning evidence are kept separate.
                  </p>
                  <h4>Skills in your profile</h4>
                  <div className="tag-row">
                    {profile.skills.map(s => (
                      <span>{s} · Self-reported</span>
                    ))}
                  </div>
                  <h4>Learning completed</h4>
                  <div className="tag-row">
                    {completed.map(id => (
                      <span className="tag-green">
                        {lessons.find(l => l.id === id)?.skill} · Completed
                      </span>
                    ))}
                  </div>
                  <h4>Demonstrated project skills</h4>
                  {project.submitted ? (
                    <div className="project-portfolio">
                      <Award size={18} />
                      <div>
                        <b>{project.title}</b>
                        <span>Submitted project · Feedback available</span>
                      </div>
                    </div>
                  ) : (
                    <p className="muted">
                      Submit your first project to add practical evidence here.
                    </p>
                  )}
                </section>
                <section className="panel">
                  <h3>Portfolio highlights</h3>
                  <div className="portfolio-stat">
                    <b>{completed.length}</b>
                    <span>Learning modules completed</span>
                  </div>
                  <div className="portfolio-stat">
                    <b>{project.submitted ? '1' : '0'}</b>
                    <span>Projects submitted</span>
                  </div>
                  <div className="portfolio-stat">
                    <b>{skillScore}%</b>
                    <span>Current skill overlap</span>
                  </div>
                  <div className="sample-note">
                    <ShieldCheck size={14} /> Profile skills are not
                    independently verified.
                  </div>
                </section>
              </div>
            </>
          )}
          {page === 'Opportunities' && (
            <>
              <div className="opportunity-intro panel">
                <div>
                  <div className="eyebrow">YOUR EARN STAGE</div>
                  <h2>Find opportunities that fit your next step.</h2>
                  <p className="muted">
                    Matches use your profile skills and completed learning
                    modules. Listings below are sample data.
                  </p>
                </div>
                <div className="opportunity-icon">
                  <BriefcaseBusiness size={30} />
                </div>
              </div>
              <div className="filter-row">
                <span>3 curated opportunities</span>
                <span className="sample-tag">
                  SAMPLE LISTINGS · NOT LIVE VACANCIES
                </span>
              </div>
              <div className="opportunity-list">
                {jobs.map((j, i) => (
                  <div className="panel opportunity-card">
                    <div className="opportunity-card-top">
                      <div className="company-mark large">
                        {j.company.slice(0, 1)}
                      </div>
                      <div className="job-main">
                        <h3>{j.title}</h3>
                        <span>
                          {j.company} · {j.type}
                        </span>
                      </div>
                      <div className="opportunity-match">
                        <b>{match(j.skills)}%</b>
                        <span>skill match</span>
                      </div>
                    </div>
                    <div className="opportunity-meta">
                      <span>
                        <BriefcaseBusiness size={14} />
                        {j.level}
                      </span>
                      <span>
                        <Target size={14} />
                        {j.location}
                      </span>
                    </div>
                    <div className="tag-row">
                      {j.skills.map(s => (
                        <span
                          className={
                            profile.skills.includes(s) ||
                            completed.some(id =>
                              lessons
                                .find(l => l.id === id)
                                ?.skill.toLowerCase()
                                .includes(s.toLowerCase().split(' ')[0])
                            )
                              ? 'tag-green'
                              : ''
                          }
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                    <div className="opportunity-footer">
                      <span>
                        {
                          j.skills.filter(s => !profile.skills.includes(s))
                            .length
                        }{' '}
                        listed skills not yet in your profile
                      </span>
                      <button
                        className="text-link"
                        onClick={() =>
                          notify(
                            'This is a sample opportunity. No external application is available.'
                          )
                        }
                      >
                        View details <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
          <footer className="page-footer">
            <span>© 2026 Elevora AI</span>
            <span>
              <ShieldCheck size={13} /> Demo workspace · Progress saved in this
              browser
            </span>
            <span>Learn. Prove. Earn.</span>
          </footer>
        </div>
      </main>
      {notice && (
        <div className="toast">
          <CheckCircle2 size={17} />
          {notice}
        </div>
      )}
    </div>
  );
}
export default App;
