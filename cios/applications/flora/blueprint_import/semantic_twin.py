"""Typed, read-only semantic projection over staged import candidates."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import re


@dataclass(frozen=True)
class SemanticObject:
    record_id: str
    kind: str
    statement: str
    subject: str
    evidence_refs: tuple[str, ...]
    freshness: str
    confidence: str
    governance: str
    source_file: str
    source_location: str
    eligible_conclusion: bool
    exclusion_reason: str = ""
    original_id: str = ""
    references: tuple[str, ...] = ()
    sufficiency: str = "unsupported claim"
    permitted_use: str = "not eligible for prominence"
    consequence: str = ""
    domains: tuple[str, ...] = ()
    affected_organisations: tuple[str, ...] = ()
    attributes: Mapping[str, Any] | None = None
    validation_status: str = "accepted"
    residual_reason: str = ""


@dataclass(frozen=True)
class SemanticEnterprise:
    # The imported business-object identity used by relationship endpoints.
    identity_key: str
    # A navigation identity only; never relationship evidence.
    presentation_key: str
    name: str
    aliases: tuple[str, ...]
    records: tuple[SemanticObject, ...]
    # Governed import lineage.  These are deliberately distinct from the
    # presentation key: a candidate record ID identifies the staged row while
    # the original/source ID is the endpoint vocabulary used by Relationships.
    source_identity: str = ""
    candidate_identity: str = ""
    relationship_subject_identity: str = ""
    ambiguous: bool = False
    unresolved_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticTwin:
    objects: tuple[SemanticObject, ...]
    enterprises: tuple[SemanticEnterprise, ...]
    unresolved_references: tuple[str, ...] = ()

    def of_kind(self, kind: str) -> tuple[SemanticObject, ...]:
        return tuple(o for o in self.objects if o.kind == kind)


@dataclass(frozen=True)
class TwinCollection:
    """A navigation projection; its members remain immutable semantic objects."""
    key: str
    label: str
    description: str
    objects: tuple[SemanticObject, ...]


@dataclass(frozen=True)
class ExecutiveRecordViewModel:
    """Canonical semantic-owner output consumed by imported Twin pages.

    This is deliberately a projection of ``SemanticObject.attributes`` rather
    than the Researcher ``source_payload``.  The import adapter owns vocabulary
    translation; this contract only selects already-canonical fields for a
    business object and gives them stable presentation labels.
    """
    record_id: str
    kind: str
    title: str
    fields: tuple[tuple[str, Any], ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedRelationship:
    """Resolution result for a governed standalone Relationship object."""
    relationship: SemanticObject
    source_id: str
    target_id: str
    relationship_type: str
    source: SemanticObject | None
    target: SemanticObject | None
    status: str = "candidate relationship unresolved"
    reason: str = "endpoint missing"

    @property
    def resolved(self) -> bool:
        return self.status.endswith("relationship resolved")


@dataclass(frozen=True)
class SubjectAssociation:
    """One resolved relationship returned by the import-scoped read boundary."""
    relationship_id: str
    relationship_type: str
    direction: str
    subject_endpoint: str
    related_endpoint: str
    related_business_object_id: str
    related_business_object_family: str
    resolution_state: str
    related_object: SemanticObject


@dataclass(frozen=True)
class EvidenceApplicability:
    """Explain one canonical Evidence-to-Enterprise applicability path."""
    evidence: SemanticObject
    verdict: str
    path: str


def evidence_subject(evidence: SemanticObject) -> str:
    """Return the stable primary subject supplied by the Evidence owner.

    Evidence registers use ``supported_object`` for the object the source is
    about.  Its first value is the primary subject; subsequent values retain
    additional content scope and can establish applicability, but do not
    change whose company disclosure the Evidence is.
    """
    if evidence.kind != "evidence":
        return ""
    supplied = str((evidence.attributes or {}).get("supported_object") or evidence.subject or "").strip()
    return next((part.strip() for part in re.split(r"[;/]", supplied) if part.strip()), "")


def evidence_publisher(evidence: SemanticObject) -> str:
    """Return the supplied publisher without treating it as Evidence subject."""
    return str((evidence.attributes or {}).get("publisher") or "").strip() if evidence.kind == "evidence" else ""


def evidence_subject_matches_enterprise(evidence: SemanticObject, ent: SemanticEnterprise) -> bool:
    """Whether the Evidence's *primary* subject is the dossier Enterprise."""
    identities = {ent.name.casefold(), ent.identity_key.casefold(), ent.source_identity.casefold(),
                  ent.relationship_subject_identity.casefold(), *(alias.casefold() for alias in ent.aliases)}
    identities.discard("")
    return evidence_subject(evidence).casefold() in identities


# These rules describe which endpoint is the Enterprise association subject;
# locating a subject at either endpoint does not make arbitrary edges symmetric.
ASSOCIATION_DIRECTIONS: Mapping[str, tuple[str, str]] = {
    "Enterprise owns Programme": ("source", "transformation_programme"),
    "Opportunity targets Enterprise": ("target", "opportunity"),
}


EXECUTIVE_FIELDS: Mapping[str, tuple[tuple[str, str], ...]] = {
    "industry_twin": (
        ("Industry profile", "industry_profile"),
    ),
    "enterprise_twin": (
        ("Overview", "description"), ("Strategy", "strategy"),
        ("Operating structure", "operating_structure"),
        ("Financial context", "financial_context"), ("Technology", "technology"),
        ("Ecosystem", "ecosystem"), ("Pressures", "pressures"),
        ("Programmes", "programmes"), ("Transformation posture", "transformation_posture"),
    ),
    "market_participant_twin": (
        ("Role", "role"), ("Domain", "domain"), ("Capabilities", "capabilities"),
        ("Relationships", "relationships"), ("Current activity", "current_activity"),
        ("Market significance", "significance"),
    ),
    "transformation_programme": (
        ("Owner", "owner"), ("Business unit", "business_unit"),
        ("Objective", "objective"), ("Stage", "phase"), ("Timing", "timing"),
        ("Investment", "investment"),
    ),
    "opportunity_hypothesis": (
        ("Customer", "affected_enterprises"), ("Client problem", "client_problem"),
        ("Business unit", "business_unit"), ("Buyer", "buyer"),
        ("Timing", "procurement_timing"), ("Procurement status", "procurement_status"),
        ("Commercial type", "commercial_type"), ("Value type", "value_type"),
        ("Value", "value_range"),
    ),
    "ai_reinvention_assessment": (
        ("Current operating model", "summary"), ("Affected functions", "affected_functions"),
        ("AI disruption mechanism", "ai_disruption_mechanism"), ("Timing", "timing"),
        ("Expected tipping point", "expected_tipping_point"), ("Executive implications", "consequence"),
    ),
}


def executive_record_view_model(obj: SemanticObject) -> ExecutiveRecordViewModel:
    """Return the deployed-page model from canonical semantic owner output."""
    attributes = obj.attributes or {}
    fields = tuple((label, attributes[name]) for label, name in EXECUTIVE_FIELDS.get(obj.kind, ())
                   if attributes.get(name) not in (None, "", [], {}, ()))
    return ExecutiveRecordViewModel(obj.record_id, obj.kind,
                                    str(attributes.get("title") or obj.statement or obj.original_id or "Twin record"),
                                    fields, obj.evidence_refs)


# This is the single business-vocabulary mapping for imported Twin presentation.
# It deliberately lives beside semantic assembly, rather than in a web view.
BUSINESS_COLLECTIONS: Mapping[str, tuple[str, str, tuple[str, ...]]] = {
    "industry-overview": ("Industry Overview", "The governed industry context represented in this Twin.", ("industry", "industry_twin", "industry_overview")),
    "enterprises": ("Enterprise Dossiers", "Priority organisations represented in this Twin.", ("enterprise", "enterprise_twin", "enterprise_dossier", "entity")),
    "market-participants": ("Market Participants", "Other organisations shaping the market.", ("market_participant", "market_participant_twin")),
    "opportunities": ("Opportunities", "Evidence-bounded commercial hypotheses.", ("opportunity", "opportunity_hypothesis", "ranked_opportunity", "opportunity_twin")),
    "insights": ("Insights", "Material observations and interpretations.", ("executive_intelligence", "fact", "observation", "supported_interpreted_observation")),
    "financial-intelligence": ("Financial Intelligence", "Financial measures and their business interpretation.", ("financial_observation", "financial_fact", "economic_pool")),
    "transformation-programmes": ("Transformation Programmes", "Material programmes changing represented organisations.", ("transformation_programme",)),
    "reinvention-assessments": ("Reinvention Assessments", "Owner-supplied AI reinvention assessments.", ("ai_reinvention_assessment",)),
    "capabilities-and-offers": ("Capabilities and Offers", "Capabilities and offers represented in the Twin.", ("capability_offer",)),
    "relationships": ("Relationships", "Connections represented across the market.", ("relationship", "supplier_relationship")),
    "memberships": ("Memberships", "Governed collection memberships represented in the Twin.", ("membership",)),
    "evidence-sources": ("Evidence Sources", "Sources supporting the Twin.", ("evidence",)),
    "unknowns": ("Unknowns", "Important gaps retained for investigation.", ("unknown",)),
    "contradictions": ("Contradictions", "Conflicting claims requiring interpretation.", ("contradiction",)),
    "release-manifests": ("Release Manifests", "Governed release declarations for the Twin.", ("release_manifest",)),
}


def business_collections(twin: SemanticTwin, *, include_empty: bool = False,
                         domain: str = "all") -> tuple[TwinCollection, ...]:
    """Translate semantic records into distinct business concepts.

    Canonical wrapper collections own business navigation when present.  Their
    underlying semantic records remain in ``twin.objects`` for inspection; we
    never merge records by a mutable display label.
    """
    objects = tuple(o for o in twin.objects if _in_domain(o, domain))
    canonical_owner = {
        "enterprises": ("enterprise_twin" if any(o.kind == "enterprise_twin" for o in objects)
                        else "enterprise" if any(o.kind == "enterprise" for o in objects) else "entity"),
        "market-participants": "market_participant_twin" if any(o.kind == "market_participant_twin" for o in objects) else "market_participant",
        "opportunities": ("opportunity_hypothesis" if any(o.kind == "opportunity_hypothesis" for o in objects)
                          else "ranked_opportunity" if any(o.kind == "ranked_opportunity" for o in objects) else "opportunity"),
    }
    mapped = {kind for _label, _description, kinds in BUSINESS_COLLECTIONS.values() for kind in kinds}
    result = []
    for key, (label, description, kinds) in BUSINESS_COLLECTIONS.items():
        selected = tuple(o for o in objects if o.kind in kinds)
        if key in canonical_owner:
            selected = tuple(o for o in selected if o.kind == canonical_owner[key])
        if key == "insights":
            selected = tuple(o for o in selected if executive_insight_eligible(o))
        if key == "enterprises":
            # Enterprise collection membership is owned by the assembled
            # canonical identities, not by a query limit or by duplicate
            # wrapper records.  A domain lens follows the dossier's supported
            # records even when the identity wrapper itself has no domain.
            members = tuple(e for e in twin.enterprises if domain in {"", "all"} or
                            any(_in_domain(o, domain) for o in e.records))
            selected = tuple(next((o for o in e.records if o.kind == canonical_owner[key]), e.records[0])
                             for e in members if e.records)
        selected = tuple({business_object_id(o): o for o in selected}.values())
        result.append(TwinCollection(key, label, description, selected))
    other = tuple(o for o in objects if o.kind not in mapped)
    if other:
        result.append(TwinCollection("other", "Other Twin content", "Additional typed content available for advanced inspection.", other))
    return tuple(collection for collection in result if include_empty or collection.objects)


def business_object_id(obj: SemanticObject) -> str:
    """Return the immutable source/canonical identity owned by staging."""
    return obj.original_id or obj.record_id


def evidence_applicability(twin: SemanticTwin, ent: SemanticEnterprise) -> tuple[EvidenceApplicability, ...]:
    """Return only Evidence with an explicit path, retaining why it applies.

    Direct ownership comes from canonical subject/organisation identity.  A
    reference from an Enterprise-associated canonical object is an explicit
    relationship-derived path.  Regulator/market material is shared only when
    that same reference establishes applicability; global presence is never
    sufficient.
    """
    names = {ent.name.casefold(), *(a.casefold() for a in ent.aliases),
             ent.identity_key.casefold(), ent.source_identity.casefold(),
             ent.relationship_subject_identity.casefold()}
    names.discard("")
    refs: dict[str, str] = {}
    for record in ent.records:
        for ref in record.evidence_refs:
            refs.setdefault(ref.casefold(), business_object_id(record))
    rows = []
    for obj in twin.objects:
        if obj.kind != "evidence":
            continue
        identity = business_object_id(obj)
        supported = str((obj.attributes or {}).get("supported_object") or obj.subject)
        subjects = {part.strip().casefold() for part in re.split(r"[;/]", supported) if part.strip()}
        subjects.update(a.casefold() for a in obj.affected_organisations)
        direct = bool(names.intersection(subjects))
        referrer = refs.get(identity.casefold())
        attrs = obj.attributes or {}
        shared = any(term in (" ".join((obj.subject, str(attrs.get("publisher", "")),
                                        str(attrs.get("source_type", "")),
                                        str(attrs.get("supported_object", ""))))).casefold()
                     for term in ("ofcom", "regulator", "industry", "market", "infrastructure", "project gigabit", "public-sector"))
        if direct:
            primary = evidence_subject(obj)
            reason = ("canonical Evidence primary subject matches Enterprise identity" if
                      evidence_subject_matches_enterprise(obj, ent) else
                      f"Evidence content scope includes Enterprise; primary subject remains {primary or 'not supplied'}")
            rows.append(EvidenceApplicability(obj, "DIRECT", reason))
        elif referrer and shared:
            rows.append(EvidenceApplicability(obj, "SHARED-APPLICABLE", f"shared market/regulatory Evidence referenced by {referrer}"))
        elif referrer:
            rows.append(EvidenceApplicability(obj, "CROSS-ENTERPRISE-EXPLAINED", f"canonical Enterprise-associated object {referrer} references this Evidence"))
    return tuple(sorted(rows, key=lambda row: business_object_id(row.evidence)))


def evidence_for_enterprise(twin: SemanticTwin, ent: SemanticEnterprise) -> tuple[SemanticObject, ...]:
    """Resolve an Enterprise's Evidence from the import-scoped canonical owner.

    ``ent.records`` is a convenient assembled projection, not the Evidence
    owner.  Evidence remains owned by ``twin.objects`` and is resolved using
    the same governed subject/affected-organisation association and factual
    reference identities used during semantic assembly.  This also makes old
    persisted Enterprise projections usable without copying Evidence into a
    Key-Reports-specific store.
    """
    return tuple(row.evidence for row in evidence_applicability(twin, ent))


def relationship_endpoints(obj: SemanticObject) -> tuple[str, str, str]:
    """Read the existing governed relationship vocabulary."""
    if obj.kind not in {"relationship", "supplier_relationship"}:
        return "", "", ""
    attributes = obj.attributes or {}
    return (str(attributes.get("source") or attributes.get("source_id") or ""),
            str(attributes.get("target") or attributes.get("target_id") or ""),
            str(attributes.get("relationship_type") or attributes.get("type") or "Relationship"))


def resolve_relationships(twin: SemanticTwin) -> tuple[ResolvedRelationship, ...]:
    """Resolve every standalone Relationship through canonical object identity.

    Endpoint lookup is deliberately exact (apart from case): aliases and prose
    are not association evidence.  The returned unresolved rows are retained so
    diagnostics and every relationship consumer report the same truth.
    """
    # ``twin`` is assembled from one import run.  Keeping the registry local to
    # that read model is the import-scope boundary: an equal external ID in a
    # different run is never visible here.
    identity_rows: dict[str, list[SemanticObject]] = {}
    for obj in twin.objects:
        if obj.kind not in {"relationship", "supplier_relationship"}:
            identity_rows.setdefault(business_object_id(obj).casefold(), []).append(obj)
    rows = []
    for relationship in twin.objects:
        if relationship.kind not in {"relationship", "supplier_relationship"}:
            continue
        source_id, target_id, relationship_type = relationship_endpoints(relationship)
        source_matches = identity_rows.get(source_id.casefold(), [])
        target_matches = identity_rows.get(target_id.casefold(), [])
        source = source_matches[0] if len(source_matches) == 1 else None
        target = target_matches[0] if len(target_matches) == 1 else None
        if not source_id or not target_id:
            status, reason = "invalid relationship", "relationship endpoint ID absent"
        elif len(source_matches) > 1 or len(target_matches) > 1:
            status, reason = "candidate relationship unresolved", "endpoint ambiguous"
        elif not source or not target:
            status, reason = "candidate relationship unresolved", "endpoint missing"
        elif relationship_type in {"", "Relationship"}:
            status, reason = "candidate relationship unresolved", "relationship type unsupported"
        elif relationship.governance == "governed" and source.governance == "governed" and target.governance == "governed":
            status, reason = "promoted relationship resolved", "promoted endpoints resolved"
        else:
            status, reason = "candidate relationship resolved", "candidate endpoints resolved in import scope"
        rows.append(ResolvedRelationship(relationship, source_id, target_id,
                                         relationship_type, source, target,
                                         status, reason))
    return tuple(rows)


def query_subject_associations(twin: SemanticTwin, subject_id: str,
                               related_kinds: set[str] | None = None) -> tuple[SubjectAssociation, ...]:
    """Return candidate-resolved association evidence for a subject in ``twin``.

    ``twin`` is the candidate import scope.  Results retain every Relationship
    row; deduplication belongs to consumers that present business objects.
    Relationship-type rules determine the valid subject endpoint and therefore
    preserve direction rather than treating the graph as generally undirected.
    """
    subject = subject_id.casefold()
    results = []
    for row in resolve_relationships(twin):
        rule = ASSOCIATION_DIRECTIONS.get(row.relationship_type)
        if not row.resolved or not rule:
            continue
        endpoint, family = rule
        actual_subject = row.source_id if endpoint == "source" else row.target_id
        related_endpoint = row.target_id if endpoint == "source" else row.source_id
        related = row.target if endpoint == "source" else row.source
        if actual_subject.casefold() != subject or related is None:
            continue
        if related_kinds is not None and related.kind not in related_kinds:
            continue
        results.append(SubjectAssociation(
            business_object_id(row.relationship), row.relationship_type,
            "outgoing" if endpoint == "source" else "incoming",
            actual_subject, related_endpoint, business_object_id(related),
            family, row.status, related,
        ))
    return tuple(sorted(results, key=lambda result: (result.related_business_object_id,
                                                      result.relationship_id)))


def opportunity_enterprise_names(twin: SemanticTwin, opportunity: SemanticObject) -> tuple[str, ...]:
    """Project Enterprise names from governed Opportunity-target relationships.

    The relationship is the association owner. Direct fields remain package facts,
    but cannot manufacture an association when the graph has none.
    """
    opportunity_id = business_object_id(opportunity).casefold()
    names: list[str] = []
    for row in resolve_relationships(twin):
        if (not row.resolved or row.relationship_type != "Opportunity targets Enterprise"
                or row.source is None or row.target is None
                or business_object_id(row.source).casefold() != opportunity_id
                or row.target.kind not in {"enterprise", "enterprise_twin", "entity"}):
            continue
        name = str((row.target.attributes or {}).get("enterprise_name")
                   or (row.target.attributes or {}).get("organisation_name")
                   or (row.target.attributes or {}).get("name") or row.target.statement).strip()
        if name and name not in names:
            names.append(name)
    return tuple(names)


def enterprise_associations(twin: SemanticTwin, enterprise: SemanticEnterprise,
                            kinds: set[str]) -> tuple[tuple[SemanticObject, str, str], ...]:
    """Consume resolved, typed relationships for one import-scoped Enterprise.

    Direction is part of the governed relationship meaning.  In particular an
    Enterprise owns Programme edge runs Enterprise -> Programme, while an
    Opportunity targets Enterprise edge runs Opportunity -> Enterprise.  The
    consumer intentionally does not treat object prose/owner fields as edges.
    """
    objects = {business_object_id(obj).casefold(): obj for obj in twin.objects if obj.kind in kinds}
    found: dict[str, tuple[SemanticObject, str, str]] = {}

    for association in query_subject_associations(
            twin, enterprise.relationship_subject_identity or enterprise.identity_key, kinds):
        related = objects.get(association.related_business_object_id.casefold())
        if related:
            identity = business_object_id(related)
            # Executive presentation is by business-object identity.  Retain a
            # stable relationship row for its type/ID explainability.
            found.setdefault(identity, (related, association.relationship_type,
                                         association.relationship_id))
    return tuple(found[key] for key in sorted(found))


def executive_insight_eligible(obj: SemanticObject) -> bool:
    """The canonical, deliberately strict executive-insight contract."""
    excluded = {"evidence", "entity", "enterprise", "enterprise_twin", "market_participant",
                "market_participant_twin", "capability_offer", "unknown", "contradiction"}
    return bool(obj.eligible_conclusion and obj.kind not in excluded and obj.subject not in {"", "Twin scope"}
                and obj.statement and obj.consequence and obj.domains and obj.evidence_refs
                and obj.confidence and obj.freshness)


def _in_domain(obj: SemanticObject, domain: str) -> bool:
    lens = domain.casefold().replace("-", " ")
    if lens in {"", "all", "all twin"}:
        return True
    if lens == "cross domain":
        return len(obj.domains) >= 2
    return lens in obj.domains


def assemble_semantic_twin(candidates: list[dict[str, Any]]) -> SemanticTwin:
    objects = tuple(_object(c) for c in candidates)
    groups: dict[str, list[SemanticObject]] = {}
    names: dict[str, str] = {}
    ambiguous: set[str] = set()
    for candidate, obj in zip(candidates, objects):
        payload = candidate.get("payload") or {}
        kind = obj.kind.casefold()
        # Enterprise identity comes only from the authoritative enterprise
        # collection (or an explicit enterprise object in another package).
        if kind != "enterprise_twin" and not (kind == "entity" and payload.get("enterprise_id")):
            continue
        name = str(payload.get("enterprise_name") or payload.get("organisation_name") or
                   (payload.get("name") if any(x in kind for x in ("entity", "enterprise", "participant")) else "") or "").strip()
        subject = str(payload.get("subject") or "").strip()
        if not name and subject and any(x in kind for x in ("observation", "fact", "hypothesis", "opportun")):
            name = subject
        if not name:
            continue
        supplied_id = str(payload.get("enterprise_id") or payload.get("canonical_id") or "").strip()
        # ADR-012 makes the staged candidate's original external stable ID the
        # governed lineage owner.  TEL-001 supplies it as ``id`` and staging
        # preserves it as ``original_source_id``; it must not be discarded just
        # because the source payload has no redundant ``enterprise_id`` field.
        source_id = obj.original_id.strip()
        key = (supplied_id or source_id).casefold() or re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
        if payload.get("identity_status") in {"ambiguous", "unresolved"}:
            key = f"{key}:{obj.record_id}"
            ambiguous.add(key)
        groups.setdefault(key, []).append(obj); names.setdefault(key, name)
    by_id = {o.original_id: o for o in objects if o.original_id}
    enterprises = []
    unresolved_all: set[str] = set()
    for key, seed in sorted(groups.items(), key=lambda item: names[item[0]].casefold()):
        # Subject-labelled observations are attached only after an explicit
        # enterprise identity has established the dossier owner.
        contextual = [o for o in objects if o not in seed and
                      (o.subject.casefold() == names[key].casefold() or
                       names[key].casefold() in {name.casefold() for name in o.affected_organisations})]
        refs = {ref for o in seed + contextual for ref in o.references}
        resolved = [by_id[ref] for ref in refs if ref in by_id]
        missing = sorted(ref for ref in refs if ref not in by_id)
        unresolved_all.update(missing)
        associated = list({o.record_id: o for o in seed + contextual + resolved}.values())
        presentation_key = re.sub(r"[^a-z0-9]+", "-", names[key].casefold()).strip("-")
        identity_owner = seed[0]
        source_identity = identity_owner.original_id
        enterprises.append(SemanticEnterprise(
            key, presentation_key, names[key], tuple(sorted({names[key]})),
            tuple(associated), source_identity, identity_owner.record_id,
            source_identity or key, key in ambiguous, tuple(missing)))
    return SemanticTwin(objects, tuple(enterprises), tuple(sorted(unresolved_all)))


def _object(candidate: dict[str, Any]) -> SemanticObject:
    p = candidate.get("payload") or {}
    statement = next((str(p[k]).strip() for k in
                      ("statement", "summary", "description", "title", "opportunity_title")
                      if p.get(k)), "")
    declared_kind = str(candidate.get("candidate_object_class") or "unclassified")
    if declared_kind == "capability_offer" and p.get("name"):
        statement = f"{p['name']} — {statement}" if statement else str(p["name"])
    raw_value = p.get("value")
    metric_complete = raw_value is not None and all(p.get(k) not in (None, "") for k in
        ("metric", "unit", "period", "subject", "source")) and bool(p.get("business_significance") or statement)
    isolated = (not statement and raw_value is not None) or bool(statement and re.fullmatch(r"[\d.,%]+", statement))
    label_only = not statement and bool(p.get("name") or p.get("display_name"))
    evidence = p.get("evidence_refs") or p.get("evidence") or p.get("source_refs") or p.get("sources") or ()
    if isinstance(evidence, str): evidence = (evidence,)
    eligible = bool(statement) and not isolated and not label_only and (raw_value is None or metric_complete)
    reason = ""
    if isolated or (raw_value is not None and not metric_complete): reason = "Metric meaning, unit, period, subject, source or significance is incomplete"
    elif label_only: reason = "Identity or label is not an executive conclusion"
    elif not statement: reason = "No interpretable observation or claim was supplied"
    original_id = str(candidate.get("original_source_id") or p.get("id") or "")
    reference_fields = ("evidence_refs", "unknown_refs", "contradiction_refs", "unknowns", "contradictions", "transformations", "opportunities", "references",
                        "procurement_routes", "buying_centres", "supplier_relationships", "buyer_ids",
                        "affected_objects", "owners", "relationships", "capabilities")
    refs: list[str] = []
    for field in reference_fields:
        value = p.get(field) or ()
        refs.extend([value] if isinstance(value, str) else [str(v) for v in value if not isinstance(v, dict)])
    truth = str(candidate.get("truth_class") or "").casefold()
    kind = declared_kind
    consequence = next((str(p[k]).strip() for k in ("business_consequence", "industry_consequence", "why_it_matters", "consequence", "business_significance") if p.get(k)), "")
    raw_domains = p.get("domains") or p.get("subsectors") or p.get("domain") or p.get("subsector") or ()
    if not raw_domains:
        source_domains, target_domains = p.get("source_domains") or (), p.get("target_domains") or ()
        if isinstance(source_domains, str): source_domains = (source_domains,)
        if isinstance(target_domains, str): target_domains = (target_domains,)
        raw_domains = tuple(source_domains) + tuple(target_domains)
    if isinstance(raw_domains, str): raw_domains = (raw_domains,)
    domains = []
    for value in raw_domains:
        normal = str(value).casefold()
        if "telecom" in normal: domains.append("telecoms")
        elif "media" in normal: domains.append("media")
        elif "sport" in normal: domains.append("sport")
        elif normal.strip(): domains.append(normal.strip())
    affected = p.get("affected_enterprises") or p.get("affected_organisations") or p.get("affected_market_participants") or ()
    if isinstance(affected, str): affected = (affected,)
    if kind == "unknown": sufficiency, permitted = "unknown", "investigation"
    elif kind == "contradiction": sufficiency, permitted = "unresolved contradiction", "investigation"
    elif "opportun" in kind: sufficiency, permitted = "Opportunity Hypothesis", "commercial hypothesis"
    elif evidence and truth in {"evidence_backed", "fact", "verified"}: sufficiency, permitted = "supported fact", "executive understanding"
    elif evidence: sufficiency, permitted = "supported interpretation", "executive understanding"
    else: sufficiency, permitted = "unsupported claim", "not eligible for prominence"
    # Owner-specific identity fields take precedence over the generic scope
    # fallback.  In particular, an Opportunity's title is its canonical
    # display identity; the absence of a generic ``subject`` must not turn a
    # supplied opportunity into the synthetic label "Twin scope".
    subject = p.get("subject")
    if str(subject or "").strip() == "Twin scope":
        subject = None
    # The TEL-001 Evidence register already supplies its subject as
    # ``supported_object``.  Preserve that governed meaning instead of letting
    # dossier assembly/query context stand in for provenance.
    if not subject and declared_kind == "evidence":
        subject = p.get("supported_object")
    subject = subject or p.get("enterprise_name") or p.get("organisation_name")
    if not subject and declared_kind in {"opportunity", "opportunity_hypothesis", "ranked_opportunity", "opportunity_twin"}:
        subject = p.get("title") or p.get("opportunity_name") or p.get("opportunity_title")
    if not subject and declared_kind in {"industry", "industry_twin", "industry_overview"}:
        subject = p.get("industry_name") or p.get("name") or p.get("title") or p.get("id")
    if not subject and declared_kind in {"market_participant", "market_participant_twin"}:
        subject = p.get("participant_name") or p.get("organisation_name") or p.get("name") or p.get("title") or p.get("id")
    if not subject and declared_kind == "ai_reinvention_assessment":
        subject = p.get("enterprise_name") or p.get("organisation_name") or p.get("target") or p.get("id")
    if not subject and declared_kind == "transformation_programme":
        affected_for_subject = p.get("affected_enterprises") or p.get("affected_organisations") or ()
        if isinstance(affected_for_subject, str):
            affected_for_subject = (affected_for_subject,)
        subject = p.get("owner") or (affected_for_subject[0] if affected_for_subject else None) or p.get("business_unit") or p.get("title") or p.get("id")
    return SemanticObject(
        str(candidate.get("candidate_record_id") or candidate.get("original_source_id") or "candidate"),
        str(candidate.get("candidate_object_class") or "unclassified"), statement,
        str(subject or "Twin scope"),
        tuple(map(str, evidence)), str(p.get("freshness") or p.get("observation_date") or "unknown"),
        str(p.get("confidence") or "bounded/unspecified"),
        "governed" if candidate.get("governance_status") in {"governed", "accepted"} else "candidate",
        str(candidate.get("source_file") or "Imported package"), str(candidate.get("source_location") or "not supplied"),
        eligible, reason, original_id, tuple(dict.fromkeys(refs)), sufficiency, permitted,
        consequence, tuple(dict.fromkeys(domains)), tuple(map(str, affected)), dict(p),
        str(candidate.get("validation_status") or "accepted"),
        "; ".join(str(finding.get("message") or finding.get("code") or "")
                  for finding in candidate.get("validation_findings") or () if isinstance(finding, dict)),
    )
