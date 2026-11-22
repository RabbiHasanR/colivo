import type { TOC } from '@ember/component/template-only';
import Card from '../ui/card';

interface StatCardSignature {
  Element: HTMLElement;
  /** `@empty`: nothing recorded yet, so the value is grey (৳0, —). */
  Args: { label: string; value: string; note: string; empty?: boolean };
}

/** One number at the top of a home page (colivo-design/web/WebHomeEmpty.html). */
const StatCard: TOC<StatCardSignature> = <template>
  <Card class="flex flex-[1_1_170px] flex-col gap-1 p-4" ...attributes>
    <span class="text-xs text-muted">{{@label}}</span>
    <span
      class="font-display text-2xl font-semibold tabular-nums
        {{if @empty 'text-faint'}}"
    >{{@value}}</span>
    <span class="text-xs text-muted">{{@note}}</span>
  </Card>
</template>;

export default StatCard;
