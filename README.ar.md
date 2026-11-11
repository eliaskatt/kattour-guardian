# Kattour Guardian — كاتور غارديان

**Skill مفتوحة المصدر لمساعدات البرمجة بالذكاء الاصطناعي: تطوير التطبيقات والمواقع، تحسين UI/UX، مراجعة الأمان، وتقليل استهلاك توكنات سياق البرمجة غير الضرورية.**

[English](README.md) · [سياسة الأمان](SECURITY.md)

## جديد في v0.3: خادم MCP المحلي

أصبح بالإمكان ربط أدوات الفحص وتوفير سياق المشروع بمساعدات البرمجة التي تدعم **MCP عبر stdio**. الخادم للقراءة فقط، ويعمل محلياً باستخدام Python 3.10+ دون مفاتيح API أو مكتبات إضافية. يجب تنزيل المستودع كاملاً وضبط مسار مشروع مصرح به.

```bash
python /absolute/path/to/kattour-guardian/mcp_server.py --root /absolute/path/to/your-project
```

التعليمات الكاملة في [MCP.md](MCP.md). يوفر خمس أدوات لخريطة المشروع، الفحص الأمني الأولي، مراجعة HTML، اختصار السجلات، وتقديرات حجم السياق. **لا يقيس توكنات الفوترة الفعلية ولا يضمن توفيراً ثابتاً أو أماناً 100%.** تثبيت Skill فقط لا يثبّت خادم MCP تلقائياً.

## ماذا تفعل؟

1. **هندسة وبرمجة:** تحليل المشروع وبنيته، اقتراح أو تنفيذ تغييرات صغيرة قابلة للاختبار، مراجعة APIs وقواعد البيانات.
2. **UI/UX:** تصميم الواجهات وتقييم الاستخدام الحقيقي، تجاوب الجوال، حالات الأخطاء والتحميل، دعم اللغة العربية وRTL، وإمكانية الوصول.
3. **الأمان:** مراجعة المصادقة والصلاحيات وملفات الأسرار والتبعيات وأنماط البرمجة الخطرة وفق إرشادات OWASP المناسبة.
4. **الجودة والأداء:** اختبارات الانحدار والأداء وتحليل النتائج الفعلية، لا تخمين درجات أو ادعاءات غير مثبتة.
5. **تقارير واضحة:** تصنيف النتائج حسب الخطورة مع الدليل، مستوى الثقة، طريقة الإصلاح، وما لم يتم اختباره.
6. **Token Efficiency Engine:** فهرسة المشروع بأسماء الملفات والدوال أولاً، جلب مقاطع الكود المطلوبة فقط، استبعاد الملفات غير المهمة، مقارنة نسخ الملفات عبر SHA-256، وعدم تكرار محتوى لم يتغير داخل **المحادثة نفسها**.

**تنبيه:** لا يوجد فحص يضمن أن التطبيق آمن 100%، ولا يوجد كاشف نصوص يحل مكان اختبار اختراق مرخّص أو مراجعة أمنية متخصصة.

## التثبيت بعد نشر المستودع على GitHub

إذا كان لديك Node.js مناسب وAI Agent يدعم صيغة Agent Skills، نفّذ من مجلد مشروعك:

```bash
npx skills add eliaskatt/kattour-guardian --skill kattour-guardian
```

اتبع خيارات الأداة لتحديد المساعد المطلوب، مثل Codex أو Claude Code أو Cursor أو GitHub Copilot أو Gemini CLI.

**بدون npx:** انسخ مجلد `skills/kattour-guardian` بالكامل إلى مسار الـ Skills عند المساعد:

| الأداة | المسار داخل المشروع |
| --- | --- |
| Codex | `.agents/skills/kattour-guardian` |
| Claude Code | `.claude/skills/kattour-guardian` |
| GitHub Copilot | `.github/skills/kattour-guardian` |
| Cursor | `.cursor/skills/kattour-guardian` |
| Gemini CLI | `.gemini/skills/kattour-guardian` |

التوافق يعني أن الأداة **تدعم معيار Skills**، ولا يعني أن كل تطبيق دردشة يتصل تلقائياً بهذه المهارة.

## أمثلة الاستخدام

```text
Use kattour-guardian to evaluate my website's UI/UX, mobile experience,
accessibility and relevant application security controls. Show prioritized,
evidence-based findings; don't change production.
```

```text
Use kattour-guardian to build this feature with a clean architecture,
responsive UI, server-side authorization, tests and a release-readiness report.
```

## توفير التوكنات — ميزة جديدة في v0.2.0

بدل إرسال المشروع كاملاً إلى مساعد الذكاء الاصطناعي، نبدأ بخريطة صغيرة، ثم نزيد كمية الكود فقط إذا احتاجتها المهمة:

```bash
# خريطة ملفات ودوال صغيرة جداً
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode map --max-chars 3000 --metrics

# مقتطفات الكود المرتبطة بالمهمة (تحقق من الأسرار قبل مشاركة المخرجات)
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 --metrics

# إرسال الملفات التي تغيّرت فقط داخل استمرار المهمة نفسها
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 \
  --snapshot-out .guardian-cache/task.json

python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 \
  --snapshot-in .guardian-cache/task.json --snapshot-out .guardian-cache/task.json
```

**بدون وعود زائفة:** حدّ `--max-chars` هو للأحرف وليس عداد توكنات دقيقاً. حساب التوكنات الظاهر تقريبي، ولا يمكن ضمان توفير نسبة ثابتة مثل 90% لجميع المشاريع أو النماذج. ملفات الـ Snapshot تحفظ مسارات الملفات وبصماتها فقط، لكن لا تعِد استخدامها بمحادثة جديدة لم يرَ فيها المساعد السياق الأصلي. قد تبقى معلومات حساسة في بعض مقتطفات الكود رغم محاولة إخفاء الأنماط المعروفة؛ افحص المخرجات قبل مشاركتها. **لا تختصر نطاق الاختبارات الأمنية بسبب تقليل السياق.**

لضغط سجلات الأخطاء الطويلة قبل عرضها على المساعد:

```bash
python skills/kattour-guardian/scripts/log_compact.py build.log --max-chars 2500
```

التفاصيل الهندسية في [دليل تحسين التوكنات](skills/kattour-guardian/references/token-efficiency.md).

## الفحوصات المحلية

تتطلب Python 3.10 أو أحدث، ولا ترسل الشيفرة عبر الإنترنت:

```bash
# فحص مؤشرات أمنية محدودة: أسرار محتملة، تعطيل TLS، وأنماط كود حساسة
python skills/kattour-guardian/scripts/security_scan.py . --format markdown --fail-on high

# مؤشرات وصول أساسية في HTML الخام فقط
python skills/kattour-guardian/scripts/html_a11y.py . --format markdown

# التحقق من أن ملف المهارة وروابطها صالحة
python scripts/validate.py

# تشغيل الاختبارات
python -m unittest discover -s tests -v
```

**حدود هذه الأدوات:** الفحص النصي لا يكتشف كل الثغرات، ونتائجه الأولية قد تكون خاطئة؛ فحص HTML لا يختبر تجربة المستخدم أو إمكانية الوصول الكاملة في المتصفح.

## نشر المشروع على حسابك

أنشئ مستودعاً **عاماً وفارغاً** باسم `kattour-guardian` في حساب `eliaskatt` ثم نفّذ الأوامر التالية داخل مجلد المشروع المستخرج:

```bash
git init
git add .
git commit -m "Initial release: Kattour Guardian Agent Skill"
git branch -M main
git remote add origin https://github.com/eliaskatt/kattour-guardian.git
git push -u origin main
```

بعد ذلك جرّب التثبيت مع مساعدَين مختلفين وتحقق من نجاح GitHub Actions.

## الرخصة

MIT — يمكن للجميع الاستخدام والتعديل والمساهمة مع المحافظة على إشعار حقوق النشر والرخصة.
