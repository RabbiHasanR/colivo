import type { TOC } from '@ember/component/template-only';
import type { Dependency, ServerStatus } from '../../services/server-status';

interface ServerStatusSignature {
  Args: { status: ServerStatus };
}

const PART_NAMES: Record<Dependency, string> = {
  database: 'the database',
  redis: 'Redis',
};

/** The start page's words for a server status. */
export function serverStatusText(status: ServerStatus): string {
  switch (status.kind) {
    case 'connected':
      return 'Server connected';
    case 'unreachable':
      return "Can't reach the server";
    case 'degraded': {
      const parts = status.down.map((part) => PART_NAMES[part]).join(' and ');
      const verb = status.down.length === 1 ? 'is' : 'are';
      return `Server problem: ${parts} ${verb} down`;
    }
  }
}

const ServerStatusMessage: TOC<ServerStatusSignature> = <template>
  <p data-test-server-status>{{serverStatusText @status}}</p>
</template>;

export default ServerStatusMessage;
