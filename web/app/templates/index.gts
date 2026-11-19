import type { TOC } from '@ember/component/template-only';
import ServerStatusMessage from '../components/health/server-status';
import type { ServerStatus } from '../services/server-status';

const IndexTemplate: TOC<{ Args: { model: ServerStatus } }> = <template>
  <ServerStatusMessage @status={{@model}} />
</template>;

export default IndexTemplate;
