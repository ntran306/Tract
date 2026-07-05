export function AboutPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-16">
      <h1 className="font-display text-3xl font-semibold tracking-tight">About Tract</h1>
      <div className="mt-6 space-y-4 text-text-muted">
        <p>
          Tract is a portfolio manager for people who own places — a rental, an Airbnb,
          a flip in progress, or just the home they live in. It keeps the ledger: what
          came in, what went out, what it's worth, and what that means.
        </p>
        <p>
          A design choice worth being upfront about: most numbers in Tract are entered
          by you. Big listing sites don't share their data, and we'd rather have your
          real rent roll than a scraped guess. Where genuinely free public data exists —
          federal house-price indexes, HUD fair-market rents — Tract uses it, clearly
          labeled as the estimate it is.
        </p>
        <p className="text-sm">
          Tract's figures are for your own tracking — not an appraisal, tax, or
          investment advice.
        </p>
      </div>
    </main>
  )
}
