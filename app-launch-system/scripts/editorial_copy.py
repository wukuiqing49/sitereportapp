"""Localized website chrome; article prose belongs to the site's content files."""

COPY = {
    "es": {
        "feature": "Función de la aplicación|El problema que resuelve|Qué puedes hacer|Datos necesarios|Resultados|Opciones disponibles|Flujo de trabajo|Limitaciones|Preguntas frecuentes|Referencias|Leer la guía relacionada|Ruta de navegación",
        "blog": "Guías de {app}|Métodos de trabajo, preparación y comprobación de resultados.|Temas|Guías prácticas|Elige una tarea y revisa sus requisitos y resultados.|Leer artículo|Guía práctica|Tutorial|En esta página|Guías relacionadas|Ver todos los artículos|Ruta de navegación|Publicado|Autor|Resumen del tutorial|Dificultad|Básica|Pasos|Requisitos|Dispositivo Android y datos de inspección|Antes de empezar|Comprobar el resultado|Limitaciones|Qué puedes hacer|Procedimiento|Opciones que debes revisar",
        "titles": "{feature}: guía práctica de {app}|Cómo usar {feature} en {app}",
    },
    "pt": {
        "feature": "Recurso do aplicativo|Problema que resolve|O que você pode fazer|Dados necessários|Resultados|Opções disponíveis|Fluxo de trabalho|Limitações|Perguntas frequentes|Referências|Ler o guia relacionado|Caminho de navegação",
        "blog": "Guias do {app}|Fluxos de trabalho, preparação e verificação dos resultados.|Temas|Guias práticos|Escolha uma tarefa e confira seus requisitos e resultados.|Ler artigo|Guia prático|Tutorial|Nesta página|Guias relacionados|Ver todos os artigos|Caminho de navegação|Publicado|Autor|Visão geral do tutorial|Dificuldade|Básica|Etapas|Requisitos|Dispositivo Android e dados de inspeção|Antes de começar|Verificar o resultado|Limitações|O que você pode fazer|Procedimento|Opções a revisar",
        "titles": "{feature}: guia prático do {app}|Como usar {feature} no {app}",
    },
    "fr": {
        "feature": "Fonction de l’application|Le besoin|Ce que vous pouvez faire|Informations à préparer|Résultats|Options disponibles|Déroulement de l’inspection|Limites à connaître|Questions fréquentes|Références|Lire le guide associé|Fil d’Ariane",
        "blog": "Guides de {app}|Méthodes de travail, préparation et vérification des résultats.|Thèmes|Guides pratiques|Choisissez une tâche et vérifiez les prérequis et les résultats.|Lire l’article|Guide pratique|Tutoriel|Sur cette page|Guides associés|Voir tous les articles|Fil d’Ariane|Publié le|Auteur|Présentation du tutoriel|Difficulté|Débutant|Étapes|Prérequis|Appareil Android et données d’inspection|Avant de commencer|Vérifier le résultat|Limites à connaître|Ce que vous pouvez faire|Procédure|Options à vérifier",
        "titles": "{feature} : guide pratique de {app}|Comment utiliser {feature} dans {app}",
    },
    "de": {
        "feature": "App-Funktion|Das gelöste Problem|Möglichkeiten|Benötigte Angaben|Ergebnisse|Verfügbare Optionen|Arbeitsablauf|Einschränkungen|Häufige Fragen|Referenzen|Zugehörigen Leitfaden lesen|Brotkrumennavigation",
        "blog": "Anleitungen für {app}|Arbeitsabläufe, Vorbereitung und Prüfung der Ergebnisse.|Themen|Praktische Anleitungen|Wählen Sie eine Aufgabe und prüfen Sie Voraussetzungen und Ergebnisse.|Artikel lesen|Praxisleitfaden|Anleitung|Auf dieser Seite|Weitere Anleitungen|Alle Artikel ansehen|Brotkrumennavigation|Veröffentlicht|Herausgeber|Überblick|Schwierigkeit|Einfach|Schritte|Voraussetzungen|Android-Gerät und Inspektionsdaten|Vor dem Start|Ergebnis prüfen|Einschränkungen|Möglichkeiten|Vorgehensweise|Zu prüfende Optionen",
        "titles": "{feature}: Praxisleitfaden für {app}|{feature} in {app} verwenden",
    },
    "ja": {
        "feature": "アプリの機能|解決できる課題|できること|必要な情報|出力結果|設定項目|操作の流れ|制限事項|よくある質問|参考情報|関連ガイドを読む|パンくずリスト",
        "blog": "{app}の使い方|作業の手順、事前準備、結果の確認方法を紹介します。|トピック|実践ガイド|作業を選び、必要な情報と結果の確認方法を確認してください。|記事を読む|実践ガイド|操作ガイド|目次|関連ガイド|すべての記事|パンくずリスト|公開日|発行者|操作の概要|難易度|初級|手順|必要なもの|Android端末と点検データ|始める前に|結果の確認|制限事項|できること|操作手順|確認する設定",
        "titles": "{feature}：{app}の実践ガイド|{app}で{feature}を使う方法",
    },
    "ko": {
        "feature": "앱 기능|해결하는 문제|사용 가능한 기능|필요한 정보|결과|설정 항목|작업 흐름|제한 사항|자주 묻는 질문|참고 자료|관련 가이드 읽기|탐색 경로",
        "blog": "{app} 사용 가이드|작업 절차, 사전 준비 및 결과 확인 방법을 안내합니다.|주제|실무 가이드|작업을 선택하고 필요한 정보와 결과를 확인하세요.|글 읽기|실무 가이드|사용 안내|목차|관련 가이드|모든 글 보기|탐색 경로|게시일|발행자|안내 개요|난이도|초급|단계|준비 사항|Android 기기 및 점검 데이터|시작하기 전에|결과 확인|제한 사항|사용 가능한 기능|작업 절차|확인할 설정",
        "titles": "{feature}: {app} 실무 가이드|{app}에서 {feature} 사용하는 방법",
    },
    "ar": {
        "feature": "ميزة التطبيق|المشكلة التي تعالجها|ما يمكنك فعله|البيانات المطلوبة|النتائج|الخيارات المتاحة|سير العمل|القيود|الأسئلة الشائعة|المراجع|قراءة الدليل المرتبط|مسار التنقل",
        "blog": "أدلة {app}|خطوات العمل والتحضير والتحقق من النتائج.|المواضيع|أدلة عملية|اختر مهمة وراجع متطلباتها ونتائجها.|قراءة المقال|دليل عملي|شرح الخطوات|في هذه الصفحة|أدلة ذات صلة|عرض جميع المقالات|مسار التنقل|تاريخ النشر|الناشر|نظرة عامة|الصعوبة|مبتدئ|الخطوات|المتطلبات|جهاز Android وبيانات الفحص|قبل البدء|التحقق من النتيجة|القيود|ما يمكنك فعله|الإجراء|خيارات يجب مراجعتها",
        "titles": "{feature}: دليل عملي في {app}|كيفية استخدام {feature} في {app}",
    },
}

FEATURE_KEYS = "kicker problem capabilities inputs outputs options steps limitations faq evidence blog breadcrumb".split()
BLOG_KEYS = "heading intro topicNav latest latestIntro read guide tutorial contents related viewAll breadcrumb published author overview difficulty easy steps requirements android prerequisites result limitations what workflow review".split()


def localized_labels(locale: str, kind: str, app_name: str = "") -> dict[str, str] | None:
    copy = COPY.get(locale.split("-")[0].lower())
    if copy is None:
        return None
    keys = FEATURE_KEYS if kind == "feature" else BLOG_KEYS
    values = copy[kind].split("|")
    if len(keys) != len(values):
        raise ValueError(f"Incomplete {kind} labels for {locale}")
    return {key: value.format(app=app_name) for key, value in zip(keys, values)}
