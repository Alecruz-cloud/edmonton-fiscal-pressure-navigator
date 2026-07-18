MMA 616 — Group AI Project

Overview
The group project runs across the four days of the course and the week between Days 2 and 3, and ends on
Day 4 (July 4) with a capstone presentation. Working in teams of four or five, you build a working dashboard
on a data source you choose, put it to use for a week, evaluate how it performed, and present the result. You
work in Claude Code throughout, with a CLAUDE.md file as the project’s specification.

The project applies the four-step method taught in the course — Plan, Build, Use, Evaluate — end to end
on a problem your team chooses.

Weight: 40% of the course grade | Format: one shared deliverable per team | Presentation: about 20
minutes plus Q&A on Day 4 (July 4)

What you build
A dashboard built on a data source — real or synthetic — that turns it into the views, metrics, and
comparisons a specific user needs to make a decision. The data is the raw material; the value is in what the
dashboard makes visible and decidable. A good project is one where someone would actually open the
dashboard to make a decision or get work done.

You build it in an agentic workspace: a Claude Code project governed by a CLAUDE.md, with the data
connected as a real source and Claude Skills, subagents, and workflows used where they help. That workspace
is how you build the dashboard, not a layer inside it, and you walk us through it in your presentation.

You already have the technical skills to build. The project is graded on judgment rather than capability:
whether the dashboard is worth building, whether it shows what you said it would, and whether you can show
that it does. A working, deployed dashboard is required. Going further with the agentic workspace that builds
it — Claude Skills, subagents, APIs, MCP connectors, custom workflows — is rewarded where it serves the
project.

Choosing the opportunity
Decide what is worth building before you settle on a dataset. Ask who the user is, what decision the
dashboard supports, and why a dashboard is the right tool for it. Settle on one dashboard concept, then check
whether the data it needs is available and workable.

You may start from one of the datasets on the menu below; that is fine, as long as the user and the decision
drive the choice rather than the features the data happens to support. Brainstorm several ways the data could
serve a real user, then pick the one most worth building. The most common way these projects go wrong is a
clever build with no clear user and no clear decision behind it.

Deliverables and timeline
Stage
Plan

When
Day 1

Build

Day 2

Use

Gap week

Deliverable
Your project CLAUDE.md: the objective, scope, the shape of your data,
and success criteria specific enough to test later.
A deployed dashboard prototype and an evaluation baseline — a small
set of known-answer test cases and a way to check the dashboard’s
output against them.
A deployment log: what you ran, what worked, what fell short, what you
corrected, and how others reacted.

MMA 616 · Group AI Project

Page 1

Stage
Evaluate

When
Day 3

Present

Day 4

Deliverable
A deployment assessment with before-and-after evaluation results, and a
revised CLAUDE.md.
The capstone presentation and the final submission.

The final graded submission is the version you hand in at the end of Day 4, after acting on the feedback you
receive that afternoon.

The deployment week
The week between Day 2 and Day 3 is for real use, not a rehearsal. Use the dashboard to do the work you
built it for, and keep a short log: where its output was useful, where it fell short, what you overrode and why,
and how anyone you showed it to responded. One week will not produce statistics, and the project is not
graded on how much you used it. Record the episodes that taught you something, and note what each one
revealed about the dashboard and its output.

Building your own evaluation
Because a single week is thin evidence, you build your own test of the dashboard’s output. Evaluation here is
about the output, not the code: are the views and answers useful and accurate for the decision the dashboard
supports? Assemble a small set of test cases paired with the output a good answer would give, and a way to
check the dashboard against them — recomputing the numbers independently, and reviewing any narrative
output yourself rather than having a model score it. Measure a baseline on Day 2, make your improvements,
and measure again after your Day 3 revision so you can show the difference. The score itself matters less than
what it tells you about where the output is weak and what to change.

The capstone presentation
Each team has about 20 minutes to present, followed by roughly 10 minutes of questions. Two things anchor
the talk: first walk us through your agentic workspace and the reasoning behind it — the CLAUDE.md
specification, how you connected and curated the data, and the Claude Skills, subagents, and workflows you
built and why each earns its place — then give a live demonstration of the dashboard. Around those two
anchors, cover the opportunity (who it serves and what decision it supports), what happened during the
deployment week, your evaluation results before and after, and what you would do next.

Every team member presents part of the talk, and any member may be asked any question. Time is enforced,
so rehearse. Bring a recording or screenshots as a backup, but the live demonstration is the point. After the
presentations, you have time the same afternoon to act on feedback and submit a final version by the end of
the day.

Assessment
The project is worth 40% of the course grade and is evaluated on six components.

Component
Opportunity and creativity

Weight
20%

Specification (the
CLAUDE.md)

Data and context

15%

10%

What it covers
A clear user and decision, and judgment about what
decision the dashboard serves — rather than a project
built around whatever data was at hand.
A usable specification: objective, scope, what is out of
scope, the data, and testable success criteria, revised as the
project develops.
Data connected directly (file, tool, API, or connector)
rather than pasted in, kept relevant and current, with the
dashboard’s output grounded in it.

MMA 616 · Group AI Project

Page 2

Component
The build

Weight
30%

Evaluation and governance

15%

Presentation and defense

10%

What it covers
A working, deployed dashboard, and how well you used
the agentic workspace to build it: skills, subagents,
workflows, and connectors used where they help.
A real test of the output with before-and-after results, a
deployment log read for what it reveals, and sensible
human review and override points.
A clear, well-paced presentation, a reasoned walkthrough
of the agentic workspace, a working dashboard
demonstration, and accurate answers in Q&A from every
member.

A few notes on grading. We assess what the dashboard does and whether you can stand behind it, not the
elegance of your code. Limited use during a single week is not penalized; what you learned from it is. A
deployed dashboard is the baseline, and building beyond it with the agentic workspace is rewarded where it
serves the project.

All team members receive the same project grade. Individual accountability comes through the Q&A, where
any member may be asked about any part of the work, and through confidential peer-contribution ratings.

Choosing your data
Use any source your project needs, real or synthetic. A good dataset is not the cleanest one; it is one that gives
a dashboard something worth showing for a real user. Look for:

  A real user and a decision the dashboard supports.
  Enough substance for an insightful dashboard rather than a single chart — multiple dimensions,

categories, time, or several related tables.

  Data you can connect and that is documented, so your workspace reads the live source rather than a

pasted fragment.

  A scale you can work with in a week, without a heavy sign-up process.

Government of Alberta open data is allowed, and using it is good practice for the portal you will use on the
individual final. Your individual final must use a different GoA dataset and a different problem than your
group’s. If no public dataset fits, you may generate synthetic data that matches the structure you need; say in
your CLAUDE.md what is synthetic and what that means for the claims the dashboard can make.

Dataset menu
Most strong dashboards take one of four forms. Choose the kind of dashboard first, then find data that
supports it:

  Operational or monitoring dashboard — tracks a live feed, shows current status, and flags what’s

off.

  Exploratory or analytical dashboard — lets a user slice and compare across dimensions to find

patterns.

  KPI or briefing dashboard — headline metrics and trends for a decision-maker, with the numbers

that matter up top.

  Comparison or benchmarking dashboard — ranks or compares units, periods, or categories

against each other or a norm.

Five public datasets to start from:

MMA 616 · Group AI Project

Page 3

1.  Calgary 311 Service Requests (municipal operations) — 2.6 million requests since 2012, updated
through an API. A city operations lead could watch volumes by ward and category, see current
backlogs, and have spikes flagged against the recent norm.

2.  Edmonton Building Permits (municipal development) — about 236,000 permits since 2009, with
construction value and location. A developer or economic-development analyst could see where
activity is picking up, by area and quarter, on maps and trend lines.

3.  Alberta Historical Wildfire Data, 2006–2025 (provincial risk) — every recorded fire with cause,
size, location, weather, and suppression, with a published data dictionary. A risk or emergency-
planning analyst could compare this season against the 10-year norm by cause and region.
4.  Calgary Restaurant Inspections (municipal public health) — facilities, inspection dates, and

violations. An inspector could see violations by severity and a re-inspection priority view; a consumer
could check a venue’s history.

5.  Statistics Canada Labour Force Survey (federal economics) — monthly labour-market data by
industry, occupation, and demographics, with CSV files, an API, and microdata. An economist or
policy analyst could track the latest release against prior months and surface the headline shifts.

Other places to look:

  Canadian: Open Alberta, Open Edmonton, Open Calgary, Statistics Canada, Open Government

Canada.



International: CFPB Consumer Complaints, SEC EDGAR, World Bank, OECD, Our World in
Data, data.gov, NYC Open Data.

  Text and ratings: Yelp Open Dataset, Olist e-commerce, MovieLens, Amazon Reviews.
  Catalogues: Kaggle, Hugging Face, Google Dataset Search.

Links are current as of June 2026; confirm a source before relying on it. The instructor can help you scope
any candidate dataset on Day 1.

Teams and logistics

  Teams: four or five students, one shared dashboard and submission.
  Schedule: Days 1–2, Friday June 26 and Saturday June 27; deployment week; Days 3–4, Friday July 3

and Saturday July 4. 9:00 a.m. to 5:00 p.m., room ESB-236.

  Tools: Claude Code throughout. Your CLAUDE.md is the specification and the way you direct the

build.

  The instructor builds a project in parallel, on the STEP family business survey, so you can follow the

same method demonstrated live across the four days.

MMA 616 · Group AI Project

Page 4

