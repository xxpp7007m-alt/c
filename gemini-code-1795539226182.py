from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path("hazards_data.json")

st.set_page_config(
    page_title="نظام إدارة المخاطر والبلاغات",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            direction: rtl;
            text-align: right;
            background-color: #f4f7f5;
        }
        .hero-card {
            background: linear-gradient(135deg, #1b5e3a 0%, #27794d 100%);
            color: #ffffff;
            padding: 20px 24px;
            border-radius: 18px;
            margin-bottom: 18px;
            box-shadow: 0 6px 18px rgba(27, 94, 58, 0.14);
        }
        .hero-sub {
            color: #d9efe2;
            font-size: 0.92rem;
            margin-bottom: 4px;
        }
        .hero-title {
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
        }
        .hazard-card {
            background-color: #ffffff;
            border: 1px solid #e2ebe5;
            border-right: 5px solid #27794d;
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }
        .badge-high {
            display: inline-block;
            background-color: #fdecea;
            color: #b42318;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .badge-med {
            display: inline-block;
            background-color: #fef6e7;
            color: #b54708;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .badge-low {
            display: inline-block;
            background-color: #e6f4ec;
            color: #1b5e3a;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2ebe5;
            border-radius: 14px;
            padding: 12px 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def risk_level(score: int) -> tuple[str, str]:
    if score >= 15:
        return "مرتفع جداً / عالٍ", "badge-high"
    if score >= 8:
        return "متوسط", "badge-med"
    return "منخفض", "badge-low"


def default_data() -> dict:
    today = datetime.now().date().isoformat()
    return {
        "initiative_name": "مبادرة السلامة والجودة وتحسين العمليات",
        "hazards": [
            {
                "id": "HZ-101",
                "title": "تأخر استلام المستلزمات التشغيلية",
                "department": "العمليات والإمداد",
                "likelihood": 4,
                "severity": 4,
                "status": "قيد المعالجة",
                "date": today,
                "action_plan": "تحديث جدول الطلبات الوقائية وتحديد حد أدنى للمخزون.",
            },
            {
                "id": "HZ-102",
                "title": "نقص توثيق الإجراءات اليومية في الوقت الفعلي",
                "department": "الجودة والمتابعة",
                "likelihood": 3,
                "severity": 3,
                "status": "مفتوح",
                "date": today,
                "action_plan": "تفعيل نموذج تسجيل سريع في نهاية كل وردية.",
            },
            {
                "id": "HZ-103",
                "title": "انقطاع مؤقت للاتصال بالشبكة المحلية",
                "department": "تقنية المعلومات",
                "likelihood": 2,
                "severity": 3,
                "status": "مغلق",
                "date": today,
                "action_plan": "تفعيل الحفظ المحلي التلقائي ومزامنة البيانات عند عودة الاتصال.",
            },
        ],
    }


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data = default_data()
    save_data(data)
    return data


def save_data(data: dict) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if "risk_db" not in st.session_state:
    st.session_state.risk_db = load_data()

db = st.session_state.risk_db
hazards = db["hazards"]

with st.sidebar:
    st.markdown("### 🛡️ قائمة التنقل")
    page = st.radio(
        "اختر القسم",
        [
            "لوحة المعلومات",
            "إضافة خطر جديد",
            "سجل المخاطر",
            "مصفوفة المخاطر",
            "تقرير المبادرة",
        ],
    )
    st.divider()
    st.download_button(
        label="⬇️ تصدير السجل (JSON)",
        data=json.dumps(db, ensure_ascii=False, indent=2),
        file_name="hazards_export.json",
        mime="application/json",
    )

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-sub">{db.get("initiative_name", "إدارة المخاطر")} • {datetime.now().strftime("%Y-%m-%d")}</div>
        <div class="hero-title">{page}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

df = pd.DataFrame(hazards) if hazards else pd.DataFrame(
    columns=["id", "title", "department", "likelihood", "severity", "status", "date", "action_plan"]
)
if not df.empty:
    df["score"] = df["likelihood"] * df["severity"]

if page == "لوحة المعلومات":
    total_h = len(df)
    high_h = int((df["score"] >= 15).sum()) if not df.empty else 0
    open_h = int((df["status"] != "مغلق").sum()) if not df.empty else 0
    closed_h = int((df["status"] == "مغلق").sum()) if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المخاطر", total_h)
    c2.metric("مخاطر عالية (≥ 15)", high_h)
    c3.metric("قيد المتابعة / مفتوح", open_h)
    c4.metric("مغلقة / معالجة", closed_h)

    st.markdown("#### أبرز البلاغات والمخاطر المسجلة")
    for item in reversed(hazards):
        sc = item["likelihood"] * item["severity"]
        lvl, badge_cls = risk_level(sc)
        st.markdown(
            f"""
            <div class="hazard-card">
                <span class="{badge_cls}">{lvl} ({sc}/25)</span>
                <strong> — {item['title']}</strong>
                <div style="color:#55625a; margin-top:4px;">
                    القسم: {item['department']} | الحالة: {item['status']} | التاريخ: {item['date']}
                </div>
                <div style="margin-top:6px;">الإجراء المقترح: {item.get('action_plan') or 'لا يوجد'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif page == "إضافة خطر جديد":
    with st.form("add_hazard_form", clear_on_submit=True):
        h_id = st.text_input("رمز الخطر", value=f"HZ-{101 + len(hazards)}")
        h_title = st.text_input("وصف الخطر أو البلاغ", placeholder="مثال: تأخر اعتماد النماذج")
        h_dept = st.text_input("القسم / الوحدة", placeholder="مثال: الإدارة / العمليات")
        col_l, col_s = st.columns(2)
        h_like = col_l.slider("الاحتمالية (1 - 5)", min_value=1, max_value=5, value=3)
        h_sev = col_s.slider("الأثر / الخطورة (1 - 5)", min_value=1, max_value=5, value=3)
        h_status = st.selectbox("الحالة", ["مفتوح", "قيد المعالجة", "مغلق"])
        h_action = st.text_area("خطة العمل أو الإجراء الوقائي")

        if st.form_submit_button("حفظ الخطر"):
            if h_title.strip():
                hazards.append(
                    {
                        "id": h_id.strip() or f"HZ-{len(hazards) + 1}",
                        "title": h_title.strip(),
                        "department": h_dept.strip() or "عام",
                        "likelihood": int(h_like),
                        "severity": int(h_sev),
                        "status": h_status,
                        "date": datetime.now().date().isoformat(),
                        "action_plan": h_action.strip(),
                    }
                )
                save_data(db)
                st.success("تم حفظ الخطر بنجاح.")
                st.rerun()
            else:
                st.warning("يرجى إدخال وصف الخطر.")

elif page == "سجل المخاطر":
    if df.empty:
        st.info("لا توجد مخاطر مسجلة.")
    else:
        status_filter = st.selectbox("تصفية حسب الحالة", ["الكل", "مفتوح", "قيد المعالجة", "مغلق"])
        view_df = df if status_filter == "الكل" else df[df["status"] == status_filter]
        st.dataframe(view_df, use_container_width=True)

        st.markdown("#### تحديث حالة خطر")
        selected_id = st.selectbox("اختر رمز الخطر", [h["id"] for h in hazards])
        new_status = st.selectbox("الحالة الجديدة", ["مفتوح", "قيد المعالجة", "مغلق"])
        if st.button("تحديث الحالة"):
            for h in hazards:
                if h["id"] == selected_id:
                    h["status"] = new_status
                    break
            save_data(db)
            st.success("تم تحديث الحالة.")
            st.rerun()

elif page == "مصفوفة المخاطر":
    st.caption("الدرجة = الاحتمالية × الخطورة (من 1 إلى 25)")
    matrix_rows = []
    for s in range(5, 0, -1):
        row = {"الخطورة \\ الاحتمالية": f"خطورة {s}"}
        for l in range(1, 6):
            row[f"احتمال {l}"] = s * l
        matrix_rows.append(row)
    matrix_df = pd.DataFrame(matrix_rows).set_index("الخطورة \\ الاحتمالية")
    st.dataframe(matrix_df, use_container_width=True)

    if not df.empty:
        st.markdown("#### توزيع المخاطر المسجلة")
        st.bar_chart(df.set_index("id")[["score"]])

elif page == "تقرير المبادرة":
    new_init = st.text_input("اسم المبادرة", value=db.get("initiative_name", ""))
    if st.button("حفظ اسم المبادرة"):
        db["initiative_name"] = new_init.strip() or "مبادرة الجودة والسلامة"
        save_data(db)
        st.success("تم تحديث اسم المبادرة.")
        st.rerun()

    st.divider()
    total_h = len(df)
    closed_h = int((df["status"] == "مغلق").sum()) if not df.empty else 0
    rate = round((closed_h / total_h) * 100, 1) if total_h else 0.0
    st.metric("نسبة إغلاق المخاطر المسجلة", f"{rate}%", delta=f"{closed_h} من {total_h}")
    if not df.empty:
        st.dataframe(
            df[["id", "title", "department", "score", "status", "action_plan"]],
            use_container_width=True,
        )
