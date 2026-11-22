import type { TOC } from '@ember/component/template-only';
import type { Me } from '../../services/session';
import { firstName } from '../../utils/names';
import { roleLabel } from '../../utils/roles';

interface WelcomeSignature {
  /** `@month`: the month the home is in, `November 2026`. */
  Args: { me: Me; month?: string };
}

/**
 * The top of a home page (colivo-design/web/WebHomeEmpty.html): the home,
 * role and month, a greeting, and the Home ID, for support (FR-88).
 */
const Welcome: TOC<WelcomeSignature> = <template>
  <header
    class="flex flex-wrap items-end justify-between gap-3"
    data-test-welcome
  >
    <div class="flex flex-col gap-1">
      <p class="text-[13px] text-muted">
        <span data-test-welcome-home>{{@me.home.name}}</span>
        ·
        {{roleLabel @me.membership.role}}
        {{#if @month}}· <span data-test-welcome-month>{{@month}}</span>{{/if}}
      </p>
      <h1 class="text-3xl font-semibold" data-test-welcome-greeting>Welcome,
        {{firstName @me.membership.name}}</h1>
    </div>
    <p class="text-[13px] text-muted" data-test-welcome-home-id>Home ID
      {{@me.home.code}}</p>
  </header>
</template>;

export default Welcome;
