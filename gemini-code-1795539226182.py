from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path("wound_care_data.json")

st.set_page_config(
    page_title="ترتيب العناية بالجروح والمرضى",
    page_icon="🩺",
    layout="wide",
)

# تنسيق بصري مستوحى من الألوان الخضراء والبطاقات في الصورة المرفقة
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
            padding: 22px 26px;
            border-radius: 18px;
            margin-bottom: 18px;
            box-shadow: 0 6px 18px rgba(27, 94, 58, 0.14);
        }
        .hero-sub {
            color: #d9efe2;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .hero-title {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0;
        }
        .task-card {
            background-color: #ffffff;
            border: 1px solid #e2ebe5;
            border-right: 5px solid #27794d;
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }
        .badge-green {
            display: inline-block;
            background-color: #e6f4ec;
            color: #1b5e3a;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .badge-alert {
            display: inline-block;
            background-color: #fdecea;
            color: #b42318;
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


def default_data() -> dict:
    today = datetime.now().date()
    return {
        "patients": [
            {
                "id": "PT-101",
                "name": "مريض تجريبي 1",
                "room": "جناح أ - 102",
                "turning_interval_hours": 2,
                "last_turned_at": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                "wounds": [
                    {
                        "id": "W-1",
                        "location": "أسفل الظهر (العصعص)",
                        "wound_type": "قرحة ضغط",
                        "assessments": [
                            {
                                "date": (today - timedelta(days=10)).isoformat(),
                                "length_cm": 5.0,
                                "width_cm": 4.0,
                                "depth_cm": 1.2,
                                "exudate": "متوسط",
                                "notes": "بداية المتابعة السريرية",
                            },
                            {
                                "date": (today - timedelta(days=5)).isoformat(),
                                "length_cm": 4.2,
                                "width_cm": 3.5,
                                "depth_cm": 0.9,
                                "exudate": "خفيف",
                                "notes": "تحسن في حواف الجرح",
                            },
                            {
                                "date": today.isoformat(),
                                "length_cm": 3.4,
                                "width_cm": 3.0,
                                "depth_cm": 0.6,
                                "exudate": "خفيف جداً",
                                "notes": "استجابة جيدة للعناية والغيارات",
                            },
                        ],
                        "procedures": [
                            {
                                "date": (today - timedelta(days=5)).isoformat(),
                                "procedure": "تنظيف الجرح وتغيير الغيار الطبي",
                                "performed_by": "فريق التمريض",
                            },
                            {
                                "date": today.isoformat(),
                                "procedure": "تقييم الجرح وتحديث قياسات المساحة",
                                "performed_by": "فريق التمريض",
                            },
                        ],
                    }
                ],
            }
        ]
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


if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# الشريط الجانبي: قائمة المرضى وإضافة مريض جديد
with st.sidebar:
    st.markdown("### 🌿 قائمة المرضى")
    patient_labels = {
        f"{p['name']} ({p['id']})": p["id"] for p in db["patients"]
    }

    selected_patient_id = None
    if patient_labels:
        selected_label = st.selectbox("اختر المريض", list(patient_labels.keys()))
        selected_patient_id = patient_labels[selected_label]
    else:
        st.info("لا يوجد مرضى مسجلون حالياً.")

    st.divider()
    st.markdown("### ➕ إضافة مريض جديد")
    with st.form("add_patient_form", clear_on_submit=True):
        p_id = st.text_input("رقم الملف", placeholder="مثال: PT-102")
        p_name = st.text_input("اسم المريض")
        p_room = st.text_input("الغرفة / القسم", placeholder="مثال: جناح ب - 204")
        p_interval = st.number_input(
            "فترة التقليب (ساعات)", min_value=1, max_value=12, value=2
        )
        if st.form_submit_button("حفظ المريض"):
            if p_id.strip() and p_name.strip():
                if any(p["id"] == p_id.strip() for p in db["patients"]):
                    st.error("رقم الملف موجود مسبقاً.")
                else:
                    db["patients"].append(
                        {
                            "id": p_id.strip(),
                            "name": p_name.strip(),
                            "room": p_room.strip() or "غير محدد",
                            "turning_interval_hours": int(p_interval),
                            "last_turned_at": datetime.now().isoformat(),
                            "wounds": [],
                        }
                    )
                    save_data(db)
                    st.success("تمت إضافة المريض.")
                    st.rerun()
            else:
                st.warning("أدخل رقم الملف واسم المريض.")

    st.divider()
    st.download_button(
        label="⬇️ تصدير البيانات (JSON)",
        data=json.dumps(db, ensure_ascii=False, indent=2),
        file_name="wound_care_export.json",
        mime="application/json",
    )

if not selected_patient_id:
    st.stop()

patient = next(p for p in db["patients"] if p["id"] == selected_patient_id)

# ترويسة خضراء مستوحاة من التصميم المرفق
now_str = datetime.now().strftime("%Y-%m-%d — %H:%M")
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-sub">متابعة العناية بالجروح والمرضى • {now_str}</div>
        <div class="hero-title">{patient['name']} — {patient['room']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# مؤقت التقليب والمؤشرات السريعة
last_turned = datetime.fromisoformat(patient["last_turned_at"])
interval = timedelta(hours=patient.get("turning_interval_hours", 2))
next_turn = last_turned + interval
remaining = next_turn - datetime.now()

c1, c2, c3, c4 = st.columns(4)
c1.metric("فترة التقليب", f"كل {patient.get('turning_interval_hours', 2)} ساعات")
c2.metric("آخر تقليب", last_turned.strftime("%H:%M"))

if remaining.total_seconds() <= 0:
    overdue_mins = int(abs(remaining.total_seconds()) // 60)
    c3.metric("حالة التقليب", "متأخر عن الموعد", delta=f"-{overdue_mins} د", delta_color="inverse")
else:
    rem_mins = int(remaining.total_seconds() // 60)
    c3.metric("الوقت المتبقي", f"{rem_mins // 60} س و {rem_mins % 60} د")

c4.metric("عدد الجروح", len(patient["wounds"]))
if c4.button("✅ تسجيل إتمام التقليب الآن"):
    patient["last_turned_at"] = datetime.now().isoformat()
    save_data(db)
    st.rerun()

# إضافة جرح جديد
with st.expander("➕ إضافة جرح جديد للمريض"):
    with st.form("add_wound_form", clear_on_submit=True):
        w_location = st.text_input("موقع الجرح", placeholder="مثال: الكعب الأيمن")
        w_type = st.selectbox(
            "نوع الجرح",
            ["قرحة ضغط", "جرح جراحي", "قرحة وعائية / سكري", "رض أو سحجة", "أخرى"],
        )
        init_length = st.number_input("الطول (سم)", min_value=0.1, value=2.5, step=0.1)
        init_width = st.number_input("العرض (سم)", min_value=0.1, value=2.0, step=0.1)
        init_depth = st.number_input("العمق (سم)", min_value=0.0, value=0.5, step=0.1)
        init_notes = st.text_area("ملاحظات أولية")
        if st.form_submit_button("إضافة الجرح") and w_location.strip():
            wound_id = f"W-{len(patient['wounds']) + 1}"
            today_str = datetime.now().date().isoformat()
            patient["wounds"].append(
                {
                    "id": wound_id,
                    "location": w_location.strip(),
                    "wound_type": w_type,
                    "assessments": [
                        {
                            "date": today_str,
                            "length_cm": float(init_length),
                            "width_cm": float(init_width),
                            "depth_cm": float(init_depth),
                            "exudate": "متوسط",
                            "notes": init_notes.strip() or "تقييم أولي عند الإضافة",
                        }
                    ],
                    "procedures": [
                        {
                            "date": today_str,
                            "procedure": "فتح سجل الجرح وتسجيل التقييم الأولي",
                            "performed_by": "الفريق السريري",
                        }
                    ],
                }
            )
            save_data(db)
            st.success("تمت إضافة الجرح.")
            st.rerun()

if not patient["wounds"]:
    st.info("لا توجد جروح مسجلة لهذا المريض بعد.")
    st.stop()

wound_options = {
    f"{w['location']} — {w['wound_type']} ({w['id']})": w["id"]
    for w in patient["wounds"]
}
selected_wound_label = st.selectbox("اختر الجرح لمتابعته", list(wound_options.keys()))
selected_wound_id = wound_options[selected_wound_label]
wound = next(w for w in patient["wounds"] if w["id"] == selected_wound_id)

tab1, tab2, tab3 = st.tabs(
    ["📋 التقييم ومنحنى المساحة", "🩺 سجل الإجراءات", "📝 إضافة تقييم أو إجراء"]
)

with tab1:
    df = pd.DataFrame(wound["assessments"])
    df["area_cm2"] = (df["length_cm"] * df["width_cm"]).round(2)

    latest = df.iloc[-1]
    first = df.iloc[0]
    area_change = round(float(latest["area_cm2"]) - float(first["area_cm2"]), 2)

    m1, m2, m3 = st.columns(3)
    m1.metric("المساحة الحالية", f"{latest['area_cm2']} سم²")
    m2.metric("التغير الكلي في المساحة", f"{area_change} سم²", delta=f"{area_change} سم²")
    m3.metric("الإفرازات الأخيرة", latest["exudate"])

    st.markdown("#### منحنى تطور مساحة الجرح (سم²)")
    st.line_chart(df.set_index("date")[["area_cm2"]])

    st.markdown("#### بطاقات التقييمات السابقة")
    for row in reversed(df.to_dict(orient="records")):
        st.markdown(
            f"""
            <div class="task-card">
                <span class="badge-green">{row['date']}</span>
                <strong> — المساحة: {row['area_cm2']} سم²</strong>
                <div>الطول: {row['length_cm']} سم | العرض: {row['width_cm']} سم | العمق: {row['depth_cm']} سم | الإفرازات: {row['exudate']}</div>
                <div style="color:#55625a; margin-top:4px;">{row.get('notes') or 'بدون ملاحظات إضافية'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab2:
    if wound["procedures"]:
        for proc in reversed(wound["procedures"]):
            st.markdown(
                f"""
                <div class="task-card">
                    <span class="badge-green">{proc['date']}</span>
                    <strong> — {proc['procedure']}</strong>
                    <div style="color:#55625a; margin-top:4px;">القائم بالإجراء: {proc['performed_by']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("لا توجد إجراءات مسجلة لهذا الجرح.")

with tab3:
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### تسجيل تقييم جديد")
        with st.form("add_assessment_form", clear_on_submit=True):
            a_date = st.date_input("التاريخ", value=datetime.now().date())
            a_len = st.number_input("الطول (سم)", min_value=0.0, value=float(latest["length_cm"]), step=0.1)
            a_wid = st.number_input("العرض (سم)", min_value=0.0, value=float(latest["width_cm"]), step=0.1)
            a_dep = st.number_input("العمق (سم)", min_value=0.0, value=float(latest["depth_cm"]), step=0.1)
            a_exu = st.selectbox("الإفرازات", ["لا يوجد", "خفيف جداً", "خفيف", "متوسط", "غزير"])
            a_notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ التقييم"):
                wound["assessments"].append(
                    {
                        "date": a_date.isoformat(),
                        "length_cm": float(a_len),
                        "width_cm": float(a_wid),
                        "depth_cm": float(a_dep),
                        "exudate": a_exu,
                        "notes": a_notes.strip(),
                    }
                )
                save_data(db)
                st.success("تم حفظ التقييم.")
                st.rerun()

    with c_right:
        st.markdown("#### تسجيل إجراء أو غيار")
        with st.form("add_procedure_form", clear_on_submit=True):
            pr_date = st.date_input("التاريخ", value=datetime.now().date(), key="proc_date")
            pr_name = st.text_input("نوع الإجراء", placeholder="مثال: تنظيف وتغيير غيار")
            pr_by = st.text_input("القائم بالإجراء", placeholder="مثال: ممرض/ة القسم")
            if st.form_submit_button("حفظ الإجراء"):
                if pr_name.strip():
                    wound["procedures"].append(
                        {
                            "date": pr_date.isoformat(),
                            "procedure": pr_name.strip(),
                            "performed_by": pr_by.strip() or "غير محدد",
                        }
                    )
                    save_data(db)
                    st.success("تم تسجيل الإجراء.")
                    st.rerun()
                else:
                    st.warning("أدخل نوع الإجراء.")
