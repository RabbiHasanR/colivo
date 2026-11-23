import type { TOC } from '@ember/component/template-only';
import type { HomeChoice } from '../services/current-home';
import ChooseHomePage from '../components/homes/choose-home-page';

const ChooseHome: TOC<{ Args: { model: HomeChoice[] } }> = <template>
  <ChooseHomePage @homes={{@model}} />
</template>;

export default ChooseHome;
