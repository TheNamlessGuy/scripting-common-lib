class BaseCommunication {
  constructor() { throw Error(`${this.constructor.name} is abstract`); }

  /**
   * @returns {void}
   */
  static init() {
    browser.runtime.onConnect.addListener(this._onConnect);
  }

  /**
   * @param {BrowserPort} port
   * @param {Record<string, any>} msg
   * @returns {(port: BrowserPort, msg: Record<string, any>) => void|null}
   */
  static getAction(port, msg) {
    throw Error(`${this.constructor.name} hasn't implemented BaseCommunication::getAction`);
  }

  /**
   * @type {Object.<string, BrowserPort>}
   */
  static _ports = {}
  /**
   * @type {Object.<string, [(port: BrowserPort) => void>]}
   */
  static _onPortGet = {}

  /**
   * @param {string} name The name of the port
   * @returns {Promise<BrowserPort>}
   */
  static _getPort(name) {
    return new Promise((resolve) => {
      if (this._ports[name] != null) {
        resolve(this._ports[name]);
        return;
      }

      if (name in this._onPortGet) {
        this._onPortGet[name].push(resolve);
      } else {
        this._onPortGet[name] = [resolve];
      }
    });
  }

  /**
   * @param {BrowserPort} port
   * @returns {void}
   */
  static _onConnect(port) {
    this._ports[port.name] = port;
    port.onMessage.addListener((msg) => {
      const action = this.getAction(port, msg);
      if (action != null) {
        action(port, msg);
      } else {
        console.error(`Unknown action gotten in ${this.constructor.name}::_onConnect`, {name: port.name, msg});
      }
    });

    if (port.name in this._onPortGet) {
      for (const resolve of this._onPortGet[port.name]) {
        resolve(port);
      }

      delete this._onPortGet[port.name];
    }
  }

  /**
   * @param {string} oldName
   * @param {string} newName
   * @returns {void}
   */
  static _renamePort(oldName, newName) {
    const port = this._ports[oldName];
    port.name = newName;
    delete this._ports[oldName];
    this._ports[newName] = port;
  }

  /**
   * @param {string} name The name of the port to remove
   * @returns {void}
   */
  static _removePort(name) {
    delete this._ports[name];
  }

  /**
   * @param {string} name The name of the port
   * @param {string} action What action to perform
   * @param {Record<string, any>} data The data to pass along with the action
   * @returns {Promise<void>}
   */
  static async _performAction(name, action, data) {
    const port = await this._getPort(name);
    if (port != null) {
      port.postMessage({action: action, ...JSON.parse(JSON.stringify(data))});
    }
  }
}