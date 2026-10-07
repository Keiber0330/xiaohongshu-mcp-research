"""Generate two practice mock exams (A and B) plus answer keys for
ECN 164 Assignment 1, Part I (Chapter 2: quotes, cross rates, bid-ask
spreads, triangular arbitrage).

All numbers in the answer keys are computed here, so questions and
solutions always agree.  Run:  python3 make_mocks.py
"""
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent
FONT_DIR = "/usr/share/fonts/truetype/liberation/"
for name, file in [("Serif", "Regular"), ("Serif-Bold", "Bold"),
                   ("Serif-Italic", "Italic"), ("Serif-BoldItalic", "BoldItalic")]:
    pdfmetrics.registerFont(TTFont(name, f"{FONT_DIR}LiberationSerif-{file}.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-Italic", boldItalic="Serif-BoldItalic")

TITLE = ParagraphStyle("t", fontName="Serif-Bold", fontSize=15, leading=19, alignment=TA_CENTER)
SUB = ParagraphStyle("s", fontName="Serif", fontSize=10.5, leading=14, alignment=TA_CENTER)
BODY = ParagraphStyle("b", fontName="Serif", fontSize=11, leading=15, spaceAfter=3)
PART = ParagraphStyle("p", parent=BODY, leftIndent=22, firstLineIndent=-14)
SOL = ParagraphStyle("so", parent=BODY, leftIndent=22, fontSize=10.5, leading=14)


def m(x):
    """Money, 2 decimals with thousands separators."""
    return f"{x:,.2f}"


def r(x, d=4):
    return f"{x:,.{d}f}"


def pct(x, d=2):
    return f"{x * 100:.{d}f}%"


def pct_change(new, old):
    return (new - old) / old


# Conceptual answers shared by both versions.
CASH_SPREAD_REASONS = (
    "Any two of: (1) cash transactions are small, so the fixed cost of each trade "
    "(staff, rent at the airport, the kiosk's own profit) is spread over few dollars; "
    "(2) physical currency must be stored, shipped, insured and protected, which is "
    "costly; (3) cash trading is much less liquid/competitive than the interbank market "
    "(travelers have few alternatives at the airport), so dealers face more inventory "
    "risk and can charge more.")


# --------------------------------------------------------------------------
# Version A
# --------------------------------------------------------------------------
def mock_a():
    Q = []  # list of (points, question_paragraphs, solution_paragraphs)

    # 1. Flipping a quote
    aud, cad = 0.6550, 0.7250
    Q.append((5, [
        "<b>Flipping a quote.</b> On October 2, 2026 the Australian dollar was worth about "
        f"USD{aud:.4f}/AUD and the Canadian dollar about USD{cad:.4f}/CAD.",
        "a. How many Australian dollars does one U.S. dollar buy (AUD/USD)?",
        "b. How many Canadian dollars does one U.S. dollar buy (CAD/USD)?",
        "c. Which currency is the “base” currency in each of the original quotes?",
    ], [
        f"a. AUD/USD = 1 / {aud:.4f} = <b>AUD{r(1/aud)}/USD</b>.",
        f"b. CAD/USD = 1 / {cad:.4f} = <b>CAD{r(1/cad)}/USD</b>.",
        "c. The base currency is the one being priced (in the denominator): the <b>AUD</b> in "
        "USD/AUD and the <b>CAD</b> in USD/CAD. The USD is the quote (pricing) currency in both.",
    ]))

    # 2. Paying in foreign currency
    room, s0, s1 = 180_000, 1380.0, 1395.0
    Q.append((5, [
        "<b>Paying in a foreign currency.</b> You are traveling in South Korea and your hotel "
        f"costs ₩{room:,} (KRW) per night. The exchange rate is KRW{s0:,.0f}/USD.",
        "a. What is the cost of one night in dollars?",
        f"b. A week later the rate is KRW{s1:,.0f}/USD. Did the won appreciate or depreciate "
        "against the dollar? What does the same room cost in dollars now?",
    ], [
        f"a. {room:,} / {s0:,.0f} = <b>${m(room/s0)}</b> per night.",
        f"b. One dollar now buys more won ({s0:,.0f} → {s1:,.0f}), so the won "
        f"<b>depreciated</b> against the dollar. New cost: {room:,} / {s1:,.0f} = "
        f"<b>${m(room/s1)}</b> — the room is cheaper for a dollar holder.",
    ]))

    # 3. Bid-ask dollar cost
    need, bid, ask = 5_000_000, 9.4150, 9.4200
    Q.append((5, [
        "Nordic Furniture Imports, Inc. needs to buy 5,000,000 Swedish kronor (SEK) to pay its "
        f"Swedish supplier. Its banker quotes bid–ask rates of SEK{bid:.4f}–{ask:.4f}/USD. "
        "What will be the dollar cost of the SEK5,000,000?",
    ], [
        "The quote prices the dollar: the bank buys USD at SEK9.4150 (bid) and sells USD at "
        "SEK9.4200 (ask). The company buys SEK by <i>selling</i> dollars to the bank, so it gets "
        "the bank's bid for dollars — the rate that gives the company fewer kronor per dollar.",
        f"Dollar cost = {need:,} / {bid:.4f} = <b>${m(need/bid)}</b>.",
        f"(Check: using {ask:.4f} would give ${m(need/ask)}, a lower cost — the bank never "
        "gives the customer the better rate.)",
    ]))

    # 4. Rates of change
    p0, p1 = 0.6620, 0.6550
    a_chg = pct_change(p1, p0)
    u_chg = pct_change(1/p1, 1/p0)
    Q.append((7, [
        f"<b>Rates of change.</b> The Australian dollar was USD{p0:.4f}/AUD on September 25, "
        f"2026 and USD{p1:.4f}/AUD one week later.",
        "a. By what percentage did the Australian dollar appreciate or depreciate against the dollar?",
        "b. By what percentage did the U.S. dollar appreciate or depreciate against the Australian "
        "dollar? (Hint: first express the rates as AUD/USD.)",
        "c. Why are your answers to (a) and (b) not exactly the same size?",
    ], [
        f"a. ({p1:.4f} − {p0:.4f}) / {p0:.4f} = <b>{pct(a_chg)}</b>: the AUD "
        f"<b>depreciated</b> by {pct(-a_chg)}.",
        f"b. AUD/USD: 1/{p0:.4f} = {r(1/p0)} and 1/{p1:.4f} = {r(1/p1)}. "
        f"Change = ({r(1/p1)} − {r(1/p0)}) / {r(1/p0)} = <b>+{pct(u_chg)}</b>: the USD "
        f"<b>appreciated</b> by {pct(u_chg)}.",
        "c. Each percentage change is measured relative to a different base (the starting "
        "price of a different currency). Since USD/AUD and AUD/USD are reciprocals, "
        "1 + %Δ(AUD/USD) = 1 / (1 + %Δ(USD/AUD)), which is not linear, so the two "
        "changes are close but not equal in size.",
    ]))

    # 5. Cross rates
    eur, aud5, cny, sek = 1.16, 0.655, 7.12, 9.40
    Q.append((8, [
        f"<b>Cross rates.</b> Use the following quotes against the U.S. dollar: USD{eur:.2f}/EUR, "
        f"USD{aud5:.3f}/AUD, CNY{cny:.2f}/USD, SEK{sek:.2f}/USD.",
        "a. Calculate the cross rate between the Australian dollar and the euro, in AUD/EUR and in EUR/AUD.",
        "b. Calculate the yuan–euro cross rate (CNY/EUR).",
        "c. Calculate the Swedish krona–Australian dollar cross rate (SEK/AUD).",
        "d. Explain in one or two sentences why the dollar is called a “vehicle currency.”",
    ], [
        f"a. AUD/EUR = (USD/EUR) / (USD/AUD) = {eur:.2f} / {aud5:.3f} = <b>{r(eur/aud5)}</b>; "
        f"EUR/AUD = {aud5:.3f} / {eur:.2f} = <b>{r(aud5/eur)}</b>.",
        f"b. CNY/EUR = (CNY/USD) × (USD/EUR) = {cny:.2f} × {eur:.2f} = <b>{r(cny*eur)}</b>.",
        f"c. SEK/AUD = (SEK/USD) × (USD/AUD) = {sek:.2f} × {aud5:.3f} = <b>{r(sek*aud5)}</b>.",
        "d. Most currencies trade actively only against the dollar, so a trade between two "
        "other currencies (e.g., AUD into SEK) is usually done in two legs through the dollar. "
        "The dollar is the “vehicle” that carries the trade, because its markets are the "
        "most liquid and cheapest to use.",
    ]))

    # 6. Interbank bid-ask
    gb, ga, gq = 1.3318, 1.3322, 2_000_000
    Q.append((7, [
        f"<b>Bid–ask spreads in the interbank market.</b> A dealer quotes the British pound at "
        f"USD{gb:.4f}–{ga:.4f}/GBP.",
        "a. Which rate is the bid and which is the ask? Which rate do you get if you buy pounds "
        "from the dealer? If you sell pounds to the dealer?",
        "b. What is the spread in pips? What is the spread as a percentage of the ask price?",
        "c. A company buys GBP2,000,000 from the dealer and, after changing its mind, sells the "
        "pounds back to the dealer a minute later at the same quotes. How many dollars does the "
        "company lose?",
    ], [
        f"a. Bid = {gb:.4f} (the dealer buys GBP), ask = {ga:.4f} (the dealer sells GBP). "
        f"You <b>buy</b> pounds at the ask, USD{ga:.4f}; you <b>sell</b> pounds at the bid, USD{gb:.4f}.",
        f"b. Spread = {ga:.4f} − {gb:.4f} = 0.0004 = <b>4 pips</b>. "
        f"Percentage spread = 0.0004 / {ga:.4f} = <b>{pct((ga-gb)/ga, 4)}</b>.",
        f"c. Pays {gq:,} × {ga:.4f} = ${m(gq*ga)}; receives {gq:,} × {gb:.4f} = "
        f"${m(gq*gb)}. Loss = <b>${m(gq*(ga-gb))}</b> (= GBP2,000,000 × 0.0004).",
    ]))

    # 7. Airport kiosk
    kb, ka, usd = 1.25, 1.40, 1500
    gbp_got = usd / ka
    Q.append((6, [
        f"<b>Bid–ask spreads at the airport.</b> At the airport, a currency kiosk buys pounds at "
        f"USD{kb:.2f}/GBP and sells pounds at USD{ka:.2f}/GBP.",
        "a. What is the percentage spread? Compare it with your answer to Problem 6(b).",
        f"b. You exchange ${usd:,} into pounds at the kiosk, then change your mind and exchange "
        "all the pounds back into dollars. How many dollars do you end up with?",
        "c. Give two reasons why spreads for cash (“physical exchange”) are so much larger "
        "than interbank spreads.",
    ], [
        f"a. ({ka:.2f} − {kb:.2f}) / {ka:.2f} = <b>{pct((ka-kb)/ka)}</b>, roughly "
        f"{(ka-kb)/ka / ((ga-gb)/ga):,.0f} times the interbank spread of {pct((ga-gb)/ga, 4)}.",
        f"b. Buy pounds at the ask: {usd:,} / {ka:.2f} = GBP{m(gbp_got)}. Sell them at the bid: "
        f"{m(gbp_got)} × {kb:.2f} = <b>${m(gbp_got*kb)}</b> (a loss of ${m(usd - gbp_got*kb)}).",
        f"c. {CASH_SPREAD_REASONS}",
    ]))

    # 8. Flipping a bid-ask quote
    cb, ca = 0.7995, 0.8005
    Q.append((5, [
        f"<b>Flipping a bid–ask quote.</b> A bank quotes the dollar at CHF{cb:.4f}–{ca:.4f}/USD. "
        "What are the bank's bid and ask prices for the Swiss franc, quoted in USD/CHF? "
        "(Hint: remember that the bank always buys low and sells high.)",
    ], [
        "When the bank buys CHF it is selling USD, which it does at its USD ask (CHF0.8005 per "
        "dollar); when it sells CHF it is buying USD at its USD bid (CHF0.7995).",
        f"Bid for CHF = 1 / {ca:.4f} = <b>USD{r(1/ca, 5)}/CHF</b>; "
        f"ask for CHF = 1 / {cb:.4f} = <b>USD{r(1/cb, 5)}/CHF</b>.",
        "Check: bid &lt; ask, so the bank still buys low and sells high.",
    ]))

    # 9. Cross rate with bid-ask
    x_bid, x_ask = gb * cb, ga * ca
    Q.append((6, [
        f"<b>Cross rates with bid–ask spreads.</b> A bank quotes USD{gb:.4f}–{ga:.4f}/GBP and "
        f"CHF{cb:.4f}–{ca:.4f}/USD. A customer wants to trade pounds for Swiss francs, and the "
        "bank will go through the dollar.",
        "a. What is the bank's bid rate for pounds in terms of francs (CHF/GBP)?",
        "b. What is the bank's ask rate for pounds in terms of francs (CHF/GBP)?",
    ], [
        f"a. Bank buys GBP: the customer sells GBP for USD at the GBP bid ({gb:.4f}), then sells "
        f"those USD for CHF at the USD bid ({cb:.4f}). CHF/GBP bid = {gb:.4f} × {cb:.4f} = "
        f"<b>{r(x_bid, 6)}</b>.",
        f"b. Bank sells GBP: the customer buys USD with CHF at the USD ask ({ca:.4f}), then buys "
        f"GBP at the GBP ask ({ga:.4f}). CHF/GBP ask = {ga:.4f} × {ca:.4f} = <b>{r(x_ask, 6)}</b>.",
    ]))

    # 10. Applying the cross rate
    pay = 750_000
    mid = ((gb + ga) / 2) * ((cb + ca) / 2)
    Q.append((6, [
        f"A Swiss watch company must pay GBP{pay:,} to a British supplier. It uses the bank and "
        "the quotes in Problem 9.",
        "a. Which CHF/GBP rate applies, and how many Swiss francs will the payment cost?",
        "b. How many more francs does the company pay than it would at the mid-rates of both quotes?",
    ], [
        f"a. The company buys pounds from the bank, so it pays the bank's <b>ask</b> of "
        f"CHF{r(x_ask, 6)}/GBP. Cost = {pay:,} × {r(x_ask, 6)} = <b>CHF{m(pay*x_ask)}</b>.",
        f"b. Mid-rates: USD1.3320/GBP and CHF0.8000/USD give CHF{r(mid, 6)}/GBP, so the cost would "
        f"be CHF{m(pay*mid)}. Extra cost from the two spreads = <b>CHF{m(pay*(x_ask-mid))}</b>.",
    ]))

    # 11. Cross rate over time
    e0, e1, c0, c1 = 1.1500, 1.1700, 7.1500, 7.1000
    x0, x1 = e0 * c0, e1 * c1
    Q.append((7, [
        f"<b>Cross rates over time.</b> On September 1, 2026 the quotes were USD{e0:.4f}/EUR and "
        f"CNY{c0:.4f}/USD. On October 1, 2026 they were USD{e1:.4f}/EUR and CNY{c1:.4f}/USD.",
        "a. Calculate the CNY/EUR cross rate on both dates.",
        "b. By what percentage did the euro appreciate or depreciate against the yuan?",
        "c. By what percentage did the yuan appreciate or depreciate against the euro?",
    ], [
        f"a. Sept 1: {e0:.4f} × {c0:.4f} = <b>CNY{r(x0)}/EUR</b>. "
        f"Oct 1: {e1:.4f} × {c1:.4f} = <b>CNY{r(x1)}/EUR</b>.",
        f"b. ({r(x1)} − {r(x0)}) / {r(x0)} = <b>+{pct(pct_change(x1, x0))}</b>: the euro "
        "<b>appreciated</b> against the yuan.",
        f"c. EUR/CNY: 1/{r(x0)} = {r(1/x0, 6)} and 1/{r(x1)} = {r(1/x1, 6)}. Change = "
        f"<b>{pct(pct_change(1/x1, 1/x0))}</b>: the yuan <b>depreciated</b> by "
        f"{pct(-pct_change(1/x1, 1/x0))} against the euro.",
    ]))

    # 12. Arbitrage detection (no spreads)
    au, ja, ju = 0.6550, 99.20, 148.60
    implied = ju * au
    one = 1 / au * ja / ju
    Q.append((7, [
        "As a foreign exchange trader, you see the following quotes for Australian dollars (AUD), "
        "U.S. dollars (USD), and Japanese yen (JPY):",
        f"USD{au:.4f}/AUD    JPY{ja:.2f}/AUD    JPY{ju:.2f}/USD",
        "Is there an arbitrage opportunity, and if so, how would you exploit it? Compute your "
        "profit per $1,000,000.",
    ], [
        f"Implied JPY/AUD = (JPY/USD) × (USD/AUD) = {ju:.2f} × {au:.4f} = {r(implied)}. "
        f"The quoted rate is JPY{ja:.2f}/AUD &gt; {r(implied)}, so <b>yes</b>: the AUD is too "
        "expensive in the yen market (equivalently, yen are cheap there).",
        "Exploit it by buying AUD where it is cheap (with dollars) and selling it where it is "
        "expensive (for yen):",
        f"1) USD → AUD: 1,000,000 / {au:.4f} = AUD{m(1e6/au)}",
        f"2) AUD → JPY: × {ja:.2f} = JPY{m(1e6/au*ja)}",
        f"3) JPY → USD: / {ju:.2f} = ${m(1e6*one)}",
        f"Profit = <b>${m(1e6*(one-1))}</b> ({pct(one-1)}).",
    ]))

    # 13. Triangular arbitrage
    us_au, us_ca, ca_au = 0.6550, 0.7250, 0.9200
    imp = us_au / us_ca
    s1_ = 1e6 / us_au
    s2_ = s1_ * ca_au
    s3_ = s2_ * us_ca
    Q.append((10, [
        f"<b>Triangular arbitrage.</b> You observe the following quotes (ignore bid–ask spreads): "
        f"USD{us_au:.4f}/AUD in New York, USD{us_ca:.4f}/CAD in Toronto, and CAD{ca_au:.4f}/AUD in Sydney.",
        "a. What CAD/AUD cross rate is implied by the two dollar quotes?",
        "b. Is there an arbitrage opportunity? In which market is the Australian dollar “too expensive”?",
        "c. You start with $1,000,000. Describe the three trades you would make and calculate your "
        "profit in dollars.",
        "d. What will happen to the three exchange rates as many traders do the same thing?",
    ], [
        f"a. CAD/AUD = (USD/AUD) / (USD/CAD) = {us_au:.4f} / {us_ca:.4f} = <b>{r(imp)}</b>.",
        f"b. Yes. Sydney quotes CAD{ca_au:.4f}/AUD &gt; {r(imp)}, so the AUD is <b>too expensive in "
        "Sydney</b> (it buys more CAD there than it should).",
        f"c. 1) New York: buy AUD with USD: 1,000,000 / {us_au:.4f} = AUD{m(s1_)}. "
        f"2) Sydney: sell AUD for CAD: {m(s1_)} × {ca_au:.4f} = CAD{m(s2_)}. "
        f"3) Toronto: sell CAD for USD: {m(s2_)} × {us_ca:.4f} = ${m(s3_)}. "
        f"Profit = <b>${m(s3_-1e6)}</b>.",
        "d. Buying AUD in New York pushes USD/AUD <b>up</b>; selling AUD for CAD in Sydney pushes "
        "CAD/AUD <b>down</b>; selling CAD for USD in Toronto pushes USD/CAD <b>down</b>. The implied "
        "cross rate (USD/AUD)/(USD/CAD) rises while the Sydney rate falls, until they are equal and "
        "the profit disappears.",
    ]))

    # 14. Triangular arbitrage with spreads
    ab, aa = 0.6548, 0.6552
    cb2, ca2 = 0.7248, 0.7252
    xb, xa = 0.9020, 0.9030
    r1a = 1e6 / aa; r1b = r1a * xb; r1c = r1b * cb2
    r2a = 1e6 / ca2; r2b = r2a / xa; r2c = r2b * ab
    Q.append((10, [
        f"<b>Triangular arbitrage with bid–ask spreads.</b> Now the quotes are: "
        f"USD{ab:.4f}–{aa:.4f}/AUD, USD{cb2:.4f}–{ca2:.4f}/CAD, and CAD{xb:.4f}–{xa:.4f}/AUD. "
        "Starting with $1,000,000, check both possible routes (dollars → Australian dollars "
        "→ Canadian dollars → dollars, and dollars → Canadian dollars → Australian "
        "dollars → dollars). Is there an arbitrage profit once you pay the bid–ask spreads?",
    ], [
        "<b>Route 1: USD → AUD → CAD → USD</b>",
        f"Buy AUD at the ask: 1,000,000 / {aa:.4f} = AUD{m(r1a)}. "
        f"Sell AUD for CAD at the CAD/AUD bid: × {xb:.4f} = CAD{m(r1b)}. "
        f"Sell CAD at the USD/CAD bid: × {cb2:.4f} = <b>${m(r1c)}</b> (loss of ${m(1e6-r1c)}).",
        "<b>Route 2: USD → CAD → AUD → USD</b>",
        f"Buy CAD at the ask: 1,000,000 / {ca2:.4f} = CAD{m(r2a)}. "
        f"Buy AUD with CAD at the CAD/AUD ask: / {xa:.4f} = AUD{m(r2b)}. "
        f"Sell AUD at the USD/AUD bid: × {ab:.4f} = <b>${m(r2c)}</b> (loss of ${m(1e6-r2c)}).",
        f"<b>No arbitrage profit.</b> Both routes lose money. Equivalently, the implied CAD/AUD "
        f"bid–ask is {r(ab/ca2)}–{r(aa/cb2)} (= {ab:.4f}/{ca2:.4f} to {aa:.4f}/{cb2:.4f}), "
        f"which overlaps the quoted {xb:.4f}–{xa:.4f}, so the spreads eat any gain.",
    ]))

    # 15. Conceptual
    Q.append((6, [
        "<b>The foreign exchange market.</b> Answer briefly.",
        "a. What is “liquidity,” and why do the most-traded currency pairs (such as EUR/USD) "
        "have smaller bid–ask spreads than rarely traded pairs (such as SEK/MXN)?",
        "b. What is the interbank market, and how does it differ from the retail market in which "
        "tourists and small firms buy currency?",
        "c. A dealer does not try to predict exchange rates. How does the dealer still make a profit?",
    ], [
        "a. Liquidity is the ability to buy or sell a large amount quickly without moving the price. "
        "In heavily traded pairs, dealers can offset positions almost immediately and fixed costs are "
        "spread over huge volume, and competition among many dealers squeezes spreads; thin pairs "
        "carry more inventory risk, so dealers charge wider spreads.",
        "b. The interbank (wholesale) market is where large banks and dealers trade with each other "
        "in very large amounts (often millions of dollars) electronically or by phone at very narrow "
        "spreads. The retail market involves small transactions with end customers at much wider "
        "spreads.",
        "c. By buying at the bid and selling at the ask: the spread between the two prices is the "
        "dealer's compensation for providing immediacy and bearing inventory risk.",
    ]))
    return Q


# --------------------------------------------------------------------------
# Version B
# --------------------------------------------------------------------------
def mock_b():
    Q = []

    # 1. Flipping a quote
    nzd, chf = 0.5850, 1.2500
    Q.append((5, [
        "<b>Flipping a quote.</b> On October 2, 2026 the New Zealand dollar was worth about "
        f"USD{nzd:.4f}/NZD and the Swiss franc about USD{chf:.4f}/CHF.",
        "a. How many New Zealand dollars does one U.S. dollar buy (NZD/USD)?",
        "b. How many Swiss francs does one U.S. dollar buy (CHF/USD)?",
        "c. Which currency is the “base” currency in each of the original quotes?",
    ], [
        f"a. NZD/USD = 1 / {nzd:.4f} = <b>NZD{r(1/nzd)}/USD</b>.",
        f"b. CHF/USD = 1 / {chf:.4f} = <b>CHF{r(1/chf)}/USD</b>.",
        "c. The base currency is the one being priced (in the denominator): the <b>NZD</b> in "
        "USD/NZD and the <b>CHF</b> in USD/CHF. The USD is the quote (pricing) currency in both.",
    ]))

    # 2. Paying in foreign currency (appreciation case)
    room, s0, s1 = 2_400, 18.50, 18.20
    Q.append((5, [
        "<b>Paying in a foreign currency.</b> You are traveling in Mexico and your hotel costs "
        f"MXN{room:,} per night. The exchange rate is MXN{s0:.2f}/USD.",
        "a. What is the cost of one night in dollars?",
        f"b. A week later the rate is MXN{s1:.2f}/USD. Did the peso appreciate or depreciate "
        "against the dollar? What does the same room cost in dollars now?",
    ], [
        f"a. {room:,} / {s0:.2f} = <b>${m(room/s0)}</b> per night.",
        f"b. One dollar now buys fewer pesos ({s0:.2f} → {s1:.2f}), so the peso "
        f"<b>appreciated</b> against the dollar. New cost: {room:,} / {s1:.2f} = "
        f"<b>${m(room/s1)}</b> — the room is more expensive for a dollar holder.",
    ]))

    # 3. Bid-ask dollar cost
    need, bid, ask = 3_000_000, 1.2840, 1.2850
    Q.append((5, [
        "Lion City Electronics, Inc. needs to buy 3,000,000 Singapore dollars (SGD) to pay its "
        f"Singaporean supplier. Its banker quotes bid–ask rates of SGD{bid:.4f}–{ask:.4f}/USD. "
        "What will be the dollar cost of the SGD3,000,000?",
    ], [
        "The quote prices the dollar: the bank buys USD at SGD1.2840 (bid) and sells USD at "
        "SGD1.2850 (ask). The company buys SGD by <i>selling</i> dollars to the bank, so it gets "
        "the bank's bid for dollars — the rate that gives the company fewer SGD per dollar.",
        f"Dollar cost = {need:,} / {bid:.4f} = <b>${m(need/bid)}</b>.",
        f"(Check: using {ask:.4f} would give ${m(need/ask)}, a lower cost — the bank never "
        "gives the customer the better rate.)",
    ]))

    # 4. Rates of change (quote with USD as base)
    p0, p1 = 0.8050, 0.7930
    d_chg = pct_change(p1, p0)
    f_chg = pct_change(1/p1, 1/p0)
    Q.append((7, [
        f"<b>Rates of change.</b> The dollar was CHF{p0:.4f}/USD on September 25, 2026 and "
        f"CHF{p1:.4f}/USD one week later.",
        "a. By what percentage did the U.S. dollar appreciate or depreciate against the Swiss franc?",
        "b. By what percentage did the Swiss franc appreciate or depreciate against the dollar? "
        "(Hint: first express the rates as USD/CHF.)",
        "c. Why are your answers to (a) and (b) not exactly the same size?",
    ], [
        f"a. ({p1:.4f} − {p0:.4f}) / {p0:.4f} = <b>{pct(d_chg)}</b>: the USD "
        f"<b>depreciated</b> by {pct(-d_chg)}.",
        f"b. USD/CHF: 1/{p0:.4f} = {r(1/p0)} and 1/{p1:.4f} = {r(1/p1)}. "
        f"Change = ({r(1/p1)} − {r(1/p0)}) / {r(1/p0)} = <b>+{pct(f_chg)}</b>: the franc "
        f"<b>appreciated</b> by {pct(f_chg)}.",
        "c. Each percentage change is measured relative to a different base (the starting "
        "price of a different currency). Since CHF/USD and USD/CHF are reciprocals, "
        "1 + %Δ(USD/CHF) = 1 / (1 + %Δ(CHF/USD)), which is not linear, so the two "
        "changes are close but not equal in size.",
    ]))

    # 5. Cross rates
    gbp, nzd5, inr, mxn = 1.33, 0.585, 88.20, 18.40
    n = 10
    Q.append((8, [
        f"<b>Cross rates.</b> Use the following quotes against the U.S. dollar: USD{gbp:.2f}/GBP, "
        f"USD{nzd5:.3f}/NZD, INR{inr:.2f}/USD, MXN{mxn:.2f}/USD.",
        "a. Calculate the cross rate between the New Zealand dollar and the pound, in NZD/GBP and in GBP/NZD.",
        "b. Calculate the rupee–pound cross rate (INR/GBP).",
        "c. Calculate the peso–New Zealand dollar cross rate (MXN/NZD).",
        "d. With 10 currencies, how many exchange rates would dealers need to quote if every pair "
        "traded directly? How many if every currency traded only against the dollar? What does "
        "this tell you about the role of the dollar?",
    ], [
        f"a. NZD/GBP = (USD/GBP) / (USD/NZD) = {gbp:.2f} / {nzd5:.3f} = <b>{r(gbp/nzd5)}</b>; "
        f"GBP/NZD = {nzd5:.3f} / {gbp:.2f} = <b>{r(nzd5/gbp)}</b>.",
        f"b. INR/GBP = (INR/USD) × (USD/GBP) = {inr:.2f} × {gbp:.2f} = <b>{r(inr*gbp)}</b>.",
        f"c. MXN/NZD = (MXN/USD) × (USD/NZD) = {mxn:.2f} × {nzd5:.3f} = <b>{r(mxn*nzd5)}</b>.",
        f"d. All pairs: N(N−1)/2 = {n}×{n-1}/2 = <b>{n*(n-1)//2}</b> rates. Only against the "
        f"dollar: N−1 = <b>{n-1}</b> rates. Concentrating trade in one “vehicle currency” "
        "(the dollar) makes each of those markets far more liquid and cheap; any cross rate can be "
        "built from two dollar quotes.",
    ]))

    # 6. Interbank bid-ask
    ab, aa, aq = 0.6548, 0.6551, 5_000_000
    Q.append((7, [
        f"<b>Bid–ask spreads in the interbank market.</b> A dealer quotes the Australian dollar at "
        f"USD{ab:.4f}–{aa:.4f}/AUD.",
        "a. Which rate is the bid and which is the ask? Which rate do you get if you buy Australian "
        "dollars from the dealer? If you sell Australian dollars to the dealer?",
        "b. What is the spread in pips? What is the spread as a percentage of the ask price?",
        "c. A company buys AUD5,000,000 from the dealer and, after changing its mind, sells them "
        "back to the dealer a minute later at the same quotes. How many dollars does the company lose?",
    ], [
        f"a. Bid = {ab:.4f} (the dealer buys AUD), ask = {aa:.4f} (the dealer sells AUD). "
        f"You <b>buy</b> AUD at the ask, USD{aa:.4f}; you <b>sell</b> AUD at the bid, USD{ab:.4f}.",
        f"b. Spread = {aa:.4f} − {ab:.4f} = 0.0003 = <b>3 pips</b>. "
        f"Percentage spread = 0.0003 / {aa:.4f} = <b>{pct((aa-ab)/aa, 4)}</b>.",
        f"c. Pays {aq:,} × {aa:.4f} = ${m(aq*aa)}; receives {aq:,} × {ab:.4f} = "
        f"${m(aq*ab)}. Loss = <b>${m(aq*(aa-ab))}</b> (= AUD5,000,000 × 0.0003).",
    ]))

    # 7. Airport kiosk
    kb, ka, usd = 0.68, 0.77, 800
    cad_got = usd / ka
    Q.append((6, [
        f"<b>Bid–ask spreads at the airport.</b> At the airport, a currency kiosk buys Canadian "
        f"dollars at USD{kb:.2f}/CAD and sells Canadian dollars at USD{ka:.2f}/CAD.",
        "a. What is the percentage spread? Compare it with your answer to Problem 6(b).",
        f"b. You exchange ${usd:,} into Canadian dollars at the kiosk, then change your mind and "
        "exchange all of them back into U.S. dollars. How many U.S. dollars do you end up with?",
        "c. Give two reasons why spreads for cash (“physical exchange”) are so much larger "
        "than interbank spreads.",
    ], [
        f"a. ({ka:.2f} − {kb:.2f}) / {ka:.2f} = <b>{pct((ka-kb)/ka)}</b>, roughly "
        f"{(ka-kb)/ka / ((aa-ab)/aa):,.0f} times the interbank spread of {pct((aa-ab)/aa, 4)}.",
        f"b. Buy CAD at the ask: {usd:,} / {ka:.2f} = CAD{m(cad_got)}. Sell them at the bid: "
        f"{m(cad_got)} × {kb:.2f} = <b>${m(cad_got*kb)}</b> (a loss of ${m(usd - cad_got*kb)}).",
        f"c. {CASH_SPREAD_REASONS}",
    ]))

    # 8. Flipping a bid-ask quote
    mb, ma = 18.38, 18.42
    Q.append((5, [
        f"<b>Flipping a bid–ask quote.</b> A bank quotes the dollar at MXN{mb:.2f}–{ma:.2f}/USD. "
        "What are the bank's bid and ask prices for the Mexican peso, quoted in USD/MXN? "
        "(Hint: remember that the bank always buys low and sells high.)",
    ], [
        "When the bank buys MXN it is selling USD, which it does at its USD ask (MXN18.42 per "
        "dollar); when it sells MXN it is buying USD at its USD bid (MXN18.38).",
        f"Bid for MXN = 1 / {ma:.2f} = <b>USD{r(1/ma, 6)}/MXN</b>; "
        f"ask for MXN = 1 / {mb:.2f} = <b>USD{r(1/mb, 6)}/MXN</b>.",
        "Check: bid &lt; ask, so the bank still buys low and sells high.",
    ]))

    # 9. Cross rate with bid-ask
    x_bid, x_ask = ab * mb, aa * ma
    Q.append((6, [
        f"<b>Cross rates with bid–ask spreads.</b> A bank quotes USD{ab:.4f}–{aa:.4f}/AUD and "
        f"MXN{mb:.2f}–{ma:.2f}/USD. A customer wants to trade Australian dollars for pesos, and "
        "the bank will go through the dollar.",
        "a. What is the bank's bid rate for Australian dollars in terms of pesos (MXN/AUD)?",
        "b. What is the bank's ask rate for Australian dollars in terms of pesos (MXN/AUD)?",
    ], [
        f"a. Bank buys AUD: the customer sells AUD for USD at the AUD bid ({ab:.4f}), then sells "
        f"those USD for MXN at the USD bid ({mb:.2f}). MXN/AUD bid = {ab:.4f} × {mb:.2f} = "
        f"<b>{r(x_bid, 6)}</b>.",
        f"b. Bank sells AUD: the customer buys USD with MXN at the USD ask ({ma:.2f}), then buys "
        f"AUD at the AUD ask ({aa:.4f}). MXN/AUD ask = {aa:.4f} × {ma:.2f} = <b>{r(x_ask, 6)}</b>.",
    ]))

    # 10. Applying the cross rate (exporter receiving foreign currency)
    rec = 2_000_000
    mid = ((ab + aa) / 2) * ((mb + ma) / 2)
    Q.append((6, [
        f"A Mexican avocado exporter receives AUD{rec:,} from an Australian customer and converts "
        "it into pesos with the bank, using the quotes in Problem 9.",
        "a. Which MXN/AUD rate applies, and how many pesos does the exporter receive?",
        "b. How many fewer pesos does the exporter receive than it would at the mid-rates of both quotes?",
    ], [
        f"a. The exporter sells AUD to the bank, so it gets the bank's <b>bid</b> of "
        f"MXN{r(x_bid, 6)}/AUD. Proceeds = {rec:,} × {r(x_bid, 6)} = <b>MXN{m(rec*x_bid)}</b>.",
        f"b. Mid-rates: USD{(ab+aa)/2:.5f}/AUD and MXN{(mb+ma)/2:.2f}/USD give MXN{r(mid, 6)}/AUD, "
        f"so the proceeds would be MXN{m(rec*mid)}. Loss from the two spreads = "
        f"<b>MXN{m(rec*(mid-x_bid))}</b>.",
    ]))

    # 11. Cross rate over time
    g0, g1, i0, i1 = 1.3400, 1.3150, 87.50, 88.40
    x0, x1 = g0 * i0, g1 * i1
    Q.append((7, [
        f"<b>Cross rates over time.</b> On September 1, 2026 the quotes were USD{g0:.4f}/GBP and "
        f"INR{i0:.2f}/USD. On October 1, 2026 they were USD{g1:.4f}/GBP and INR{i1:.2f}/USD.",
        "a. Calculate the INR/GBP cross rate on both dates.",
        "b. By what percentage did the pound appreciate or depreciate against the rupee?",
        "c. By what percentage did the rupee appreciate or depreciate against the pound?",
    ], [
        f"a. Sept 1: {g0:.4f} × {i0:.2f} = <b>INR{r(x0)}/GBP</b>. "
        f"Oct 1: {g1:.4f} × {i1:.2f} = <b>INR{r(x1)}/GBP</b>.",
        f"b. ({r(x1)} − {r(x0)}) / {r(x0)} = <b>{pct(pct_change(x1, x0))}</b>: the pound "
        f"<b>depreciated</b> by {pct(-pct_change(x1, x0))} against the rupee.",
        f"c. GBP/INR: 1/{r(x0)} = {r(1/x0, 6)} and 1/{r(x1)} = {r(1/x1, 6)}. Change = "
        f"<b>+{pct(pct_change(1/x1, 1/x0))}</b>: the rupee <b>appreciated</b> against the pound. "
        "(Note that the rupee weakened against the dollar but strengthened against the pound, "
        "because the pound fell even more against the dollar.)",
    ]))

    # 12. Arbitrage detection (no spreads) -- NZD is cheap in the rupee market
    un, in_, iu = 0.5850, 50.10, 88.20
    implied = iu * un
    one = iu / in_ * un
    Q.append((7, [
        "As a foreign exchange trader, you see the following quotes for New Zealand dollars (NZD), "
        "U.S. dollars (USD), and Indian rupees (INR):",
        f"USD{un:.4f}/NZD    INR{in_:.2f}/NZD    INR{iu:.2f}/USD",
        "Is there an arbitrage opportunity, and if so, how would you exploit it? Compute your "
        "profit per $1,000,000.",
    ], [
        f"Implied INR/NZD = (INR/USD) × (USD/NZD) = {iu:.2f} × {un:.4f} = {r(implied)}. "
        f"The quoted rate is INR{in_:.2f}/NZD &lt; {r(implied)}, so <b>yes</b>: the NZD is too "
        "cheap in the rupee market.",
        "Exploit it by buying NZD where it is cheap (with rupees) and selling it where it is "
        "expensive (for dollars):",
        f"1) USD → INR: 1,000,000 × {iu:.2f} = INR{m(1e6*iu)}",
        f"2) INR → NZD: / {in_:.2f} = NZD{m(1e6*iu/in_)}",
        f"3) NZD → USD: × {un:.4f} = ${m(1e6*one)}",
        f"Profit = <b>${m(1e6*(one-1))}</b> ({pct(one-1)}).",
    ]))

    # 13. Triangular arbitrage -- pound too cheap in London
    us_gb, us_nz, nz_gb = 1.3300, 0.5850, 2.2200
    imp = us_gb / us_nz
    s1_ = 1e6 / us_nz
    s2_ = s1_ / nz_gb
    s3_ = s2_ * us_gb
    Q.append((10, [
        f"<b>Triangular arbitrage.</b> You observe the following quotes (ignore bid–ask spreads): "
        f"USD{us_gb:.4f}/GBP in New York, USD{us_nz:.4f}/NZD in Wellington, and NZD{nz_gb:.4f}/GBP in London.",
        "a. What NZD/GBP cross rate is implied by the two dollar quotes?",
        "b. Is there an arbitrage opportunity? In which market is the pound “too cheap”?",
        "c. You start with $1,000,000. Describe the three trades you would make and calculate your "
        "profit in dollars.",
        "d. What will happen to the three exchange rates as many traders do the same thing?",
    ], [
        f"a. NZD/GBP = (USD/GBP) / (USD/NZD) = {us_gb:.4f} / {us_nz:.4f} = <b>{r(imp)}</b>.",
        f"b. Yes. London quotes NZD{nz_gb:.4f}/GBP &lt; {r(imp)}, so the pound is <b>too cheap in "
        "London</b> (it costs fewer NZD there than it should).",
        f"c. 1) Wellington: buy NZD with USD: 1,000,000 / {us_nz:.4f} = NZD{m(s1_)}. "
        f"2) London: buy GBP with NZD: {m(s1_)} / {nz_gb:.4f} = GBP{m(s2_)}. "
        f"3) New York: sell GBP for USD: {m(s2_)} × {us_gb:.4f} = ${m(s3_)}. "
        f"Profit = <b>${m(s3_-1e6)}</b>.",
        "d. Buying NZD in Wellington pushes USD/NZD <b>up</b>; buying GBP with NZD in London pushes "
        "NZD/GBP <b>up</b>; selling GBP in New York pushes USD/GBP <b>down</b>. The implied cross rate "
        "(USD/GBP)/(USD/NZD) falls while the London rate rises, until they are equal and the profit "
        "disappears.",
    ]))

    # 14. Triangular arbitrage with spreads -- one route is profitable
    gb, ga = 1.3298, 1.3302
    nb, na = 0.5848, 0.5852
    xb, xa = 2.2640, 2.2660
    r1a = 1e6 / na; r1b = r1a / xa; r1c = r1b * gb
    r2a = 1e6 / ga; r2b = r2a * xb; r2c = r2b * nb
    Q.append((10, [
        f"<b>Triangular arbitrage with bid–ask spreads.</b> Now the quotes are: "
        f"USD{gb:.4f}–{ga:.4f}/GBP, USD{nb:.4f}–{na:.4f}/NZD, and NZD{xb:.4f}–{xa:.4f}/GBP. "
        "Starting with $1,000,000, check both possible routes (dollars → New Zealand dollars "
        "→ pounds → dollars, and dollars → pounds → New Zealand dollars → dollars). "
        "Is there an arbitrage profit once you pay the bid–ask spreads?",
    ], [
        "<b>Route 1: USD → NZD → GBP → USD</b>",
        f"Buy NZD at the ask: 1,000,000 / {na:.4f} = NZD{m(r1a)}. "
        f"Buy GBP with NZD at the NZD/GBP ask: / {xa:.4f} = GBP{m(r1b)}. "
        f"Sell GBP at the USD/GBP bid: × {gb:.4f} = <b>${m(r1c)}</b> (profit of ${m(r1c-1e6)}).",
        "<b>Route 2: USD → GBP → NZD → USD</b>",
        f"Buy GBP at the ask: 1,000,000 / {ga:.4f} = GBP{m(r2a)}. "
        f"Sell GBP for NZD at the NZD/GBP bid: × {xb:.4f} = NZD{m(r2b)}. "
        f"Sell NZD at the USD/NZD bid: × {nb:.4f} = <b>${m(r2c)}</b> (loss of ${m(1e6-r2c)}).",
        f"<b>Yes — Route 1 earns ${m(r1c-1e6)}</b> even after paying all three spreads. The "
        f"implied NZD/GBP bid–ask is {r(gb/na)}–{r(ga/nb)} (= {gb:.4f}/{na:.4f} to "
        f"{ga:.4f}/{nb:.4f}); the quoted ask {xa:.4f} is <i>below</i> the implied bid {r(gb/na)}, so "
        "you can buy pounds with NZD directly and sell them through the dollar for more.",
    ]))

    # 15. Conceptual
    Q.append((6, [
        "<b>The foreign exchange market.</b> Answer briefly.",
        "a. What is the interbank market, and who are its main participants?",
        "b. A customer wants to convert New Zealand dollars into Indian rupees. Why does the bank "
        "usually route the trade through the U.S. dollar even though the customer then pays two spreads?",
        "c. What is “liquidity,” and how is it related to the size of bid–ask spreads?",
    ], [
        "a. The interbank (wholesale) market is where large commercial and investment banks and "
        "dealers trade currencies with each other in very large amounts (often millions of dollars) "
        "electronically or by phone, at very narrow spreads. Smaller banks, firms and individuals "
        "reach it through these dealers.",
        "b. The NZD/INR market is thin, so a direct quote (if one exists) would have a very wide "
        "spread. NZD/USD and USD/INR are each far more liquid, so the two narrow spreads combined "
        "are usually cheaper than one wide direct spread.",
        "c. Liquidity is the ability to buy or sell a large amount quickly without moving the price. "
        "The more liquid a market, the easier it is for dealers to offset positions and the more "
        "dealers compete, so the smaller the bid–ask spread.",
    ]))
    return Q


# --------------------------------------------------------------------------
# PDF output
# --------------------------------------------------------------------------
def header(version, kind):
    story = [
        Paragraph(f"ECN 164 International Finance — Practice Mock Exam {version}", TITLE),
        Spacer(1, 4),
        Paragraph(f"{kind} · Unofficial self-study practice based on Assignment 1, Part I "
                  "(Chapter 2: quotes, cross rates, bid–ask spreads, triangular arbitrage)", SUB),
        Spacer(1, 12),
    ]
    return story


def build(version, questions):
    total = sum(p for p, _, _ in questions)
    assert total == 100, total

    # Exam
    story = header(version, "Questions")
    story.append(Paragraph(
        f"<b>Instructions.</b> {len(questions)} short-answer problems, {total} points, suggested time "
        "90 minutes. Show your work. Round exchange rates to 4 decimal places (more when a rate is "
        "very small) and money amounts to 2 decimal places. A calculator is allowed.", BODY))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Name: ________________________   Score: ______ / 100", BODY))
    story.append(Spacer(1, 10))
    for i, (pts, q, _) in enumerate(questions, 1):
        block = [Paragraph(f"<b>{i}.</b> ({pts} points) {q[0]}", BODY)]
        block += [Paragraph(line, PART) for line in q[1:]]
        block.append(Spacer(1, 10))
        story.append(KeepTogether(block))
    doc = SimpleDocTemplate(str(OUT / f"Mock_Exam_{version}.pdf"), pagesize=LETTER,
                            leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                            topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                            title=f"ECN 164 Practice Mock Exam {version}")
    doc.build(story)

    # Answer key
    story = header(version, "Answer Key")
    for i, (pts, q, sol) in enumerate(questions, 1):
        block = [Paragraph(f"<b>{i}.</b> ({pts} points) {q[0]}", BODY)]
        block += [Paragraph(line, PART) for line in q[1:]]
        block.append(Paragraph("<b><i>Solution</i></b>", SOL))
        block += [Paragraph(line, SOL) for line in sol]
        block.append(Spacer(1, 10))
        story.append(KeepTogether(block))
    doc = SimpleDocTemplate(str(OUT / f"Mock_Exam_{version}_Answer_Key.pdf"), pagesize=LETTER,
                            leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                            topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                            title=f"ECN 164 Practice Mock Exam {version} Answer Key")
    doc.build(story)


if __name__ == "__main__":
    build("A", mock_a())
    build("B", mock_b())
    print("done")
