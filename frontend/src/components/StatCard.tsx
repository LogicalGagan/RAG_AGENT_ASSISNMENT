type StatCardProps = {
  label: string;
  value: string | number;
  helper: string;
};

export function StatCard({ label, value, helper }: StatCardProps) {
  return (
    <article className="glass-card stat-card">
      <p className="eyebrow">{label}</p>
      <h3>{value}</h3>
      <p className="muted">{helper}</p>
    </article>
  );
}
