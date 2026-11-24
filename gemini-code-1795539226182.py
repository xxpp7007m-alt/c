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

# تنسيق بصري مستوحى من الألوان الخضراء والبطاقات
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

# الشريط الجانبي: قائمة المرضى وإضافة مريض جديد وإدارة البيانات
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
    st.markdown("### إدارة البيانات")
    st.download_button(
        label="⬇️ تصدير البيانات (JSON)",
        data=json.dumps(db, ensure_ascii=False, indent=2),
        file_name="wound_care_export.json",
        mime="application/json",
    )

    if st.button("🗑️ حذف جميع البيانات", type="secondary"):
        st.session_state.db = {"patients": []}
        save_data(st.session_state.db)
        st.success("تم حذف جميع البيانات.")
        st.rerun()

if not selected_patient_id:
    st.info("القائمة فارغة حالياً. أضف مريضاً جديداً من الشريط الجانبي للبدء.")
    st.stop()

patient = next(p for p in db["patients"] if p["id"] == selected_patient_id)

# ترويسة خضراء
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
