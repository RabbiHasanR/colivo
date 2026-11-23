import { module, test } from 'qunit';
import { setupTest } from 'colivo-web/tests/helpers';
import type CurrentHomeService from 'colivo-web/services/current-home';
import { LAST_HOME_KEY, TAB_HOME_KEY } from 'colivo-web/services/current-home';

const OUR_FLAT = 'our-flat-id';
const GREEN_HOUSE = 'green-house-id';

interface Owner {
  lookup(name: string): unknown;
}

function currentHome(owner: Owner): CurrentHomeService {
  return owner.lookup('service:current-home') as CurrentHomeService;
}

module('Unit | Service | current-home', function (hooks) {
  setupTest(hooks);

  const starts: [string, string | null, string | null, string | null][] = [
    // [case, this tab's home, last home chosen, expected]
    ['its own', OUR_FLAT, GREEN_HOUSE, OUR_FLAT],
    ['the last chosen', null, GREEN_HOUSE, GREEN_HOUSE],
    ['none', null, null, null],
  ];
  for (const [name, tabHome, lastHome, expected] of starts) {
    test(`a tab starts from its own home, else the last home chosen (${name})`, function (assert) {
      // GIVEN this tab's home and the last home chosen in this browser
      // WHEN  the app starts in this tab
      // THEN  it acts in this tab's home, else the last one, else none
      if (tabHome) sessionStorage.setItem(TAB_HOME_KEY, tabHome);
      if (lastHome) localStorage.setItem(LAST_HOME_KEY, lastHome);

      assert.strictEqual(currentHome(this.owner).homeId, expected);
    });
  }
});

module('Unit | Service | current-home | choosing', function (hooks) {
  setupTest(hooks);

  test('choosing a home keeps it for this tab and as the last home', function (assert) {
    // GIVEN no home chosen yet
    // WHEN  Green House is chosen
    // THEN  this tab acts in it, and it is stored for this tab and as the last home
    const service = currentHome(this.owner);

    service.choose(GREEN_HOUSE);

    assert.strictEqual(service.homeId, GREEN_HOUSE);
    assert.strictEqual(sessionStorage.getItem(TAB_HOME_KEY), GREEN_HOUSE);
    assert.strictEqual(localStorage.getItem(LAST_HOME_KEY), GREEN_HOUSE);
  });
});

module('Unit | Service | current-home | refused storage', function (hooks) {
  setupTest(hooks);

  const refuse = () => {
    throw new DOMException('Storage refused', 'SecurityError');
  };
  const real = Object.getOwnPropertyDescriptors(Storage.prototype);
  hooks.beforeEach(function () {
    Storage.prototype.getItem = refuse;
    Storage.prototype.setItem = refuse;
    Storage.prototype.removeItem = refuse;
  });
  hooks.afterEach(function () {
    Object.defineProperties(Storage.prototype, real);
  });

  test('refused storage never throws; the home is kept for the page', function (assert) {
    // GIVEN the browser refuses storage (a private window)
    // WHEN  the app starts and Green House is chosen
    // THEN  nothing throws, and this page acts in Green House
    const service = currentHome(this.owner);

    service.choose(GREEN_HOUSE);

    assert.strictEqual(service.homeId, GREEN_HOUSE);
  });
});
