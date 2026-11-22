import type { TOC } from '@ember/component/template-only';

type Tone = 'warning' | 'success';

interface NoticeSignature {
  Element: HTMLElement;
  Args: { tone: Tone; title?: string };
  Blocks: { default: [] };
}

// colivo-design/web/WebAuthErrors.html: brown for a block, teal for good news.
const TONES: Record<Tone, string> = {
  warning: 'bg-owes-tint text-owes-ink',
  success: 'bg-primary-tint text-primary-hover',
};

function classes(tone: Tone): string {
  return `flex flex-col gap-1.5 rounded-card p-4 text-sm leading-normal ${TONES[tone]}`;
}

/**
 * A tinted box that says what happened. The caller sets the role:
 * `<Notice @tone="success" role="status">New code sent</Notice>`.
 */
const Notice: TOC<NoticeSignature> = <template>
  <section class={{classes @tone}} ...attributes>
    {{#if @title}}
      <span class="text-[17px] font-semibold">{{@title}}</span>
    {{/if}}
    <span>{{yield}}</span>
  </section>
</template>;

export default Notice;
