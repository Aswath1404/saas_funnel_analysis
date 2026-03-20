# ============================================
# SaaS Funnel Analysis — Dataset Generator
# Author: Aswath
# Description: Generates synthetic B2B SaaS 
# dataset with 50,000 users, realistic funnel
# drop-off, acquisition channels, and 
# subscription data across 3 relational tables
# ============================================

import csv, random, json
from datetime import datetime, timedelta
from collections import Counter

random.seed(42)

NUM_USERS = 50000

FUNNEL = [
    "trial_started", "onboarding_completed", "project_created",
    "task_added", "teammate_invited", "integration_connected", "subscription_started",
]

# Conditional probs for non-converters (they drop somewhere before final step)
# Converters walk all the way through
BASE_COND_PROBS = [1.000, 0.750, 0.827, 0.806, 0.680, 0.706, 0.708]

COUNTRIES = ["India","USA","UK","Singapore","UAE","Others"]
COUNTRY_WEIGHTS = [0.55, 0.15, 0.10, 0.08, 0.07, 0.05]
COUNTRY_CONVERSION_MOD = {
    "India": 0.78, "USA": 1.28, "UK": 1.20,
    "Singapore": 1.22, "UAE": 1.18, "Others": 1.00
}
COUNTRY_TZ_OFFSET = {"India":5.5,"USA":-5,"UK":0,"Singapore":8,"UAE":4,"Others":0}
COUNTRY_ANNUAL_PROB = {"India":0.20,"USA":0.50,"UK":0.50,"Singapore":0.50,"UAE":0.50,"Others":0.35}

BASE_CHANNELS = ["organic_search","google_ad","linkedin_ad","content_marketing","direct"]
BASE_WEIGHTS = [0.38, 0.22, 0.18, 0.12, 0.07]
CHANNEL_CONVERSION_BOOST = {
    "organic_search":1.10,"referral":1.25,"google_ad":1.00,
    "linkedin_ad":1.08,"content_marketing":1.12,"direct":1.20,
}

COMPANY_SIZES = ["solo","small","mid","large"]
COMPANY_SIZE_WEIGHTS = [0.15,0.40,0.30,0.15]
LINKEDIN_SIZE_WEIGHTS = [0.05,0.25,0.45,0.25]
INDUSTRIES = ["tech","marketing","consulting","ecommerce","manufacturing"]
INDUSTRY_WEIGHTS = [0.35,0.20,0.18,0.17,0.10]

PLAN_BY_SIZE = {
    "solo": [("starter",0.80),("growth",0.20),("enterprise",0.00)],
    "small":[("starter",0.55),("growth",0.40),("enterprise",0.05)],
    "mid":  [("starter",0.25),("growth",0.55),("enterprise",0.20)],
    "large":[("starter",0.05),("growth",0.40),("enterprise",0.55)],
}
PLAN_MRR = {"starter":12,"growth":36,"enterprise":96}

INTEGRATIONS = ["slack","google_drive","github","jira","zapier"]
INTEGRATION_WEIGHTS = [0.35,0.25,0.18,0.12,0.10]
CHURN_REASONS = ["price","missing_features","switched_competitor","no_longer_needed"]
CHURN_WEIGHTS = [0.40,0.25,0.20,0.15]
MONTH_WEIGHTS = [0.08,0.10,0.14,0.18,0.22,0.28]

TIME_GAPS = [(0,0),(30,120),(60,1440),(5,20),(1440,7200),(4320,14400),(10080,30240)]

def pick_signup_date():
    month = random.choices(range(1,7), weights=MONTH_WEIGHTS)[0]
    return datetime(2024, month, random.randint(1,28))

def pick_plan(company_size):
    opts = PLAN_BY_SIZE[company_size]
    return random.choices([p[0] for p in opts], weights=[p[1] for p in opts])[0]

users_rows, events_rows, subscriptions_rows = [], [], []
ev_id = sess_id = sub_id = 1

print("Generating...")
for user_num in range(1, NUM_USERS+1):
    uid = f"USR_{user_num:07d}"
    signup_date = pick_signup_date()
    trial_expires = signup_date + timedelta(days=14)
    country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS)[0]
    tz = COUNTRY_TZ_OFFSET[country]
    industry = random.choices(INDUSTRIES, weights=INDUSTRY_WEIGHTS)[0]

    month = signup_date.month
    ref_w = 0.02 + (month-1)*(0.26/5)
    all_ch = BASE_CHANNELS + ["referral"]
    adj_w = [w*(1-ref_w) for w in BASE_WEIGHTS] + [ref_w]
    channel = random.choices(all_ch, weights=adj_w)[0]

    company_size = random.choices(
        COMPANY_SIZES,
        weights=LINKEDIN_SIZE_WEIGHTS if channel=="linkedin_ad" else COMPANY_SIZE_WEIGHTS
    )[0]

    conv_mod = COUNTRY_CONVERSION_MOD[country] * CHANNEL_CONVERSION_BOOST[channel]

    # Single conversion roll — preserves overall 17% target
    will_convert = random.random() < min(0.17 * conv_mod, 0.95)

    if will_convert:
        max_stage = len(FUNNEL) - 1
    else:
        # Walk through funnel until drop-off (excluding final step)
        max_stage = 0
        for i in range(1, len(FUNNEL)-1):
            if random.random() <= BASE_COND_PROBS[i]:
                max_stage = i
            else:
                break

    segment = (
        "churned_trial" if max_stage == 0 else
        "activated" if max_stage <= 2 else
        "collaborative" if max_stage <= 5 else
        "converted"
    )

    users_rows.append({
        "user_id":uid, "signup_date":signup_date.strftime("%Y-%m-%d"),
        "trial_expires_on":trial_expires.strftime("%Y-%m-%d"),
        "country":country, "acquisition_channel":channel,
        "company_size":company_size, "industry":industry, "user_segment":segment,
    })

    current_time = signup_date + timedelta(hours=random.randint(9,18), minutes=random.randint(0,59))
    cur_sess = f"SESS_{sess_id:08d}"; sess_id += 1
    sub_timestamp = sub_plan = None

    for i in range(max_stage+1):
        event_name = FUNNEL[i]
        if i > 0:
            gmin, gmax = TIME_GAPS[i]
            gap = timedelta(minutes=random.randint(gmin, gmax))
            current_time += gap
            if gap.total_seconds() > 1800:
                cur_sess = f"SESS_{sess_id:08d}"; sess_id += 1

        device = random.choices(["Web","iOS","Android"], weights=[0.60,0.22,0.18])[0]
        props = None
        if event_name == "integration_connected":
            props = json.dumps({"integration": random.choices(INTEGRATIONS, weights=INTEGRATION_WEIGHTS)[0]})
        elif event_name == "subscription_started":
            sub_plan = pick_plan(company_size)
            props = json.dumps({"plan": sub_plan})
            sub_timestamp = current_time
        elif event_name == "project_created":
            props = json.dumps({"template_used": random.choice([True,False])})
        elif event_name == "teammate_invited":
            props = json.dumps({"invites_sent": random.randint(1,5)})

        events_rows.append({
            "event_id":f"EVT_{ev_id:08d}", "user_id":uid, "session_id":cur_sess,
            "event_name":event_name, "timestamp":current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "device_type":device, "event_properties":props or "NULL",
        })
        ev_id += 1

    if will_convert and sub_timestamp and sub_plan:
        billing = "annual" if random.random() < COUNTRY_ANNUAL_PROB[country] else "monthly"
        mrr = round(PLAN_MRR[sub_plan] * (0.85 if billing=="annual" else 1.0), 2)
        is_churned = random.random() < 0.03
        churn_date = churn_reason = None
        if is_churned:
            churn_date = (sub_timestamp+timedelta(days=random.randint(60,150))).strftime("%Y-%m-%d")
            churn_reason = random.choices(CHURN_REASONS, weights=CHURN_WEIGHTS)[0]
        has_upgrade = random.random() < 0.08 and not is_churned
        upgraded_to = upgrade_date = None
        if has_upgrade:
            upgraded_to = "growth" if sub_plan=="starter" else ("enterprise" if sub_plan=="growth" else None)
            if upgraded_to:
                upgrade_date = (sub_timestamp+timedelta(days=random.randint(30,120))).strftime("%Y-%m-%d")

        subscriptions_rows.append({
            "subscription_id":f"SUB_{sub_id:07d}", "user_id":uid,
            "plan":sub_plan, "billing_cycle":billing, "mrr":mrr,
            "start_date":sub_timestamp.strftime("%Y-%m-%d"),
            "status":"churned" if is_churned else "active",
            "churned_date":churn_date or "NULL", "churn_reason":churn_reason or "NULL",
            "plan_upgraded_to":upgraded_to or "NULL", "upgrade_date":upgrade_date or "NULL",
        })
        sub_id += 1

    if user_num % 10000 == 0:
        print(f"  ⏳ {user_num:,} users done...")

def write_csv(path, rows, fields):
    with open(path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

write_csv("/mnt/user-data/outputs/users.csv", users_rows,
    ["user_id","signup_date","trial_expires_on","country","acquisition_channel","company_size","industry","user_segment"])
write_csv("/mnt/user-data/outputs/events.csv", events_rows,
    ["event_id","user_id","session_id","event_name","timestamp","device_type","event_properties"])
write_csv("/mnt/user-data/outputs/subscriptions.csv", subscriptions_rows,
    ["subscription_id","user_id","plan","billing_cycle","mrr","start_date","status","churned_date","churn_reason","plan_upgraded_to","upgrade_date"])

print(f"\n✅ DONE")
print(f"   users.csv         → {len(users_rows):,} rows")
print(f"   events.csv        → {len(events_rows):,} rows")
print(f"   subscriptions.csv → {len(subscriptions_rows):,} rows")

ec = Counter(r["event_name"] for r in events_rows)
print(f"\n📊 Funnel:")
total = ec["trial_started"]
prev = None
for e in FUNNEL:
    c = ec[e]
    pct = c/total*100
    drop = f"-{(prev-c)/prev*100:.1f}%" if prev else "—"
    print(f"  {e:<30} {c:>6,}  ({pct:.1f}%)  {drop}")
    prev = c

print(f"\n💰 Subscriptions: {len(subscriptions_rows):,} ({len(subscriptions_rows)/NUM_USERS*100:.1f}% conversion)")
sc = Counter(r["plan"] for r in subscriptions_rows)
for plan in ["starter","growth","enterprise"]:
    print(f"  {plan:<12} {sc[plan]:>5,}")
churned = sum(1 for r in subscriptions_rows if r["status"]=="churned")
print(f"  Churned:       {churned:>5,}  ({churned/max(len(subscriptions_rows),1)*100:.1f}%)")
