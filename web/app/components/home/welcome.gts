import type { TOC } from '@ember/component/template-only';
import type { Me } from '../../services/session';
import { firstName } from '../../utils/names';

interface WelcomeSignature {
  Args: { me: Me };
}

/**
 * The top of a home page (colivo-design/web/WebHomeEmpty.html): a greeting,
 * the home's name and its Home ID, for support (FR-88).
 */
const Welcome: TOC<WelcomeSignature> = <template>
  <header data-test-welcome>
    <p data-test-welcome-home>{{@me.home.name}}</p>
    <h1 data-test-welcome-greeting>Welcome,
      {{firstName @me.membership.name}}</h1>
    <p data-test-welcome-home-id>Home ID {{@me.home.code}}</p>
  </header>
</template>;

export default Welcome;
