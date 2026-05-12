/*
 * shelfEntry.ts — shared shape for chart-alternatives + chart-archive
 * entries.
 *
 * Lives under _alternatives/ because both holding zones use the same
 * entry type; _archive/<section>/index.ts files import from here too.
 * Splitting the type into a sibling _shared/ dir (e.g. charts/_shared/)
 * would conflate this holding-zone wiring with the chart-canon shared
 * helpers — keep the shelf-entry type next to the manifests that use it.
 *
 * Fields:
 *   Component       Astro component to render in the alt frame.
 *   file            Display path shown in the alt card eyebrow. Match the
 *                   on-disk path so the user can find it. For production
 *                   components kept as alts, use the production path
 *                   (e.g. "labour/Panel1LFSHeadlineIndexed.astro").
 *   title           Card title.
 *   whatDifferent   1-3 sentence "what's different from the live chart".
 *   whyBetter       1-3 sentence "why it might be better".
 *   dataFields      Compact data-source string for the card footer.
 *   data            Optional panel data passed as the `data` prop. Set
 *                   only for entries whose Component is a real production
 *                   panel that requires pipeline data to draw. Placeholder
 *                   Alt*.astro components leave this unset.
 *   pinned          Archive-only. When true, the chart-archive page
 *                   renders the entry in the Pinned zone above the rest.
 *                   Ignored by /chart-alternatives.
 *   pinnedReason    Optional short reason; shown next to the pinned star.
 *   tags            Optional free-form tags for future filtering.
 *   addedAt         Optional ISO date (YYYY-MM-DD). Used by the archive
 *                   page for sort-by-recency; absent entries sort
 *                   alphabetically by title.
 */

export interface ChartShelfEntry {
  Component: unknown;
  file: string;
  title: string;
  whatDifferent: string;
  whyBetter: string;
  dataFields: string;
  data?: unknown;
  pinned?: boolean;
  pinnedReason?: string;
  tags?: string[];
  addedAt?: string;
}
