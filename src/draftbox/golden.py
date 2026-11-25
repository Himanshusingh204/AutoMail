"""Golden set: 20 synthetic mails + automatic rubric. Rerun after any prompt/engine change."""
from .core import Msg, build_prompt, new_links, placeholders

CASES = [  # (subject, body, needs [CONFIRM])
    ("Meeting Thursday?", "Can we meet Thursday at 3pm?", True),
    ("Invoice", "Please confirm the invoice amount of 4500 is correct.", True),
    ("Thanks!", "Thanks for the help yesterday, really appreciated.", False),
    ("Quick question", "Do you know who handles billing?", False),
    ("Deadline", "Can you deliver by Friday?", True),
    ("Namaste", "Kal milte hain? Time batao.", True),
    ("Job offer", "We'd like to offer you the role. Please reply with your start date.", True),
    ("Lunch", "Lunch tomorrow?", True),
    ("Feedback", "What did you think of the proposal?", False),
    ("Refund", "I want a refund for order 1234.", True),
    ("Intro", "Hi, I'm Sam from Acme. Can we chat about a partnership?", False),
    ("Reschedule", "Can we move our call to next week?", True),
    ("Docs", "Where can I find the setup docs?", False),
    ("Price", "What's your price for 10 units?", True),
    ("Bug", "The app crashes on login, any idea?", False),
    ("Hello", "Hello, are you free?", False),
    ("Contract", "Please sign and return the contract by Monday.", True),
    ("Trip", "Are you joining the trip on the 12th?", True),
    ("Review", "Could you review my PR when you can?", False),
    ("Hinglish", "Bhai kal ka plan kya hai? Confirm karo.", True),
]


def run_golden(engine):
    bad = 0
    for subj, body, need_confirm in CASES:
        m = Msg("g", "golden", "Sam <sam@example.com>", subj, body)
        d = engine.draft(build_prompt(m, "Short, polite."))
        problems = [f"new link {x}" for x in new_links(d, body)]
        if not d.strip() or len(d) > 1500: problems.append("empty/too long")
        if need_confirm and not placeholders(d): problems.append("no [CONFIRM] placeholder")
        bad += bool(problems)
        print(("FAIL " if problems else "ok   ") + subj, "; ".join(problems))
    print(f"{len(CASES) - bad}/{len(CASES)} passed")
