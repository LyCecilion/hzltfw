from sqlalchemy import delete, or_
from sqlmodel import Session, col, select

from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun


def delete_evidence_record(session: Session, evidence_id: int) -> bool:
    evidence = session.get(EvidenceItem, evidence_id)
    if evidence is None:
        return False

    run_ids = list(
        session.exec(select(PluginRun.id).where(PluginRun.evidence_id == evidence_id))
    )
    artifact_filter = Artifact.evidence_id == evidence_id
    if run_ids:
        artifact_filter = or_(
            artifact_filter,
            col(Artifact.plugin_run_id).in_(run_ids),
        )

    session.exec(delete(Artifact).where(artifact_filter))
    session.exec(delete(PluginRun).where(PluginRun.evidence_id == evidence_id))
    session.exec(delete(EvidenceFile).where(EvidenceFile.evidence_id == evidence_id))
    session.delete(evidence)
    session.commit()
    return True


def delete_case_record(session: Session, case_id: int) -> bool:
    case = session.get(Case, case_id)
    if case is None:
        return False

    evidence_ids = list(
        session.exec(select(EvidenceItem.id).where(EvidenceItem.case_id == case_id))
    )

    session.exec(delete(Artifact).where(Artifact.case_id == case_id))
    session.exec(delete(PluginRun).where(PluginRun.case_id == case_id))
    if evidence_ids:
        session.exec(
            delete(EvidenceFile).where(col(EvidenceFile.evidence_id).in_(evidence_ids))
        )
    session.exec(delete(EvidenceItem).where(EvidenceItem.case_id == case_id))
    session.delete(case)
    session.commit()
    return True
