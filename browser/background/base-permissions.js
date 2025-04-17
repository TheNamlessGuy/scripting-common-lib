/** BrowserPermissions
 * @see https://developer.mozilla.org/docs/Mozilla/Add-ons/WebExtensions/API/permissions/Permissions
 * @typedef {object} BrowserPermissions
 * @property {string[]} [origins] An array of match patterns, representing host permissions.
 * @property {string[]} [permissions] An array of named permissions, including API permissions and clipboard permissions.
 */

class BasePermissions {
  static ADDED = 1;
  static REMOVED = 2;

  constructor() { throw Error(`${this.constructor.name} is abstract`); }

  /**
   * @returns {void}
   */
  static init() {
    browser.permissions.onAdded.addListener(this._onAdded.bind(this));
    browser.permissions.onRemoved.addListener(this._onRemoved.bind(this));
  }

  /**
   * @param {string} which
   * @param {(status: number) => void} callback
   * @returns {void}
   */
  static onChange(which, callback) {
    if (which in this._callbackMap) {
      this._callbackMap[which].push(callback);
    } else {
      this._callbackMap[which] = [callback];
    }
  }

  /**
   * @type {{[which: string]: ((status: number) => void)[]}}
   */
  static _callbackMap = {}

  /**
   * @param {string} which
   * @param {number} status
   * @returns {Promise<void>}
   */
  static async _callFor(which, status) {
    if (which in this._callbackMap) {
      for (const callback of this._callbackMap[which]) {
        await Promise.resolve(callback(status));
      }
    }
  }

  /**
   * @param {BrowserPermissions} permissions
   * @returns {Promise<void>}
   */
  static async _onAdded(permissions) {
    if ('origins' in permissions) {
      permissions.origins.forEach(x => this._callFor(x, BasePermissions.ADDED));
    }

    if ('permissions' in permissions) {
      permissions.permissions.forEach(x => this._callFor(x, BasePermissions.ADDED));
    }
  }

  /**
   * @param {BrowserPermissions} permissions
   * @returns {Promise<void>}
   */
  static async _onRemoved(permissions) {
    if ('origins' in permissions) {
      permissions.origins.forEach(x => this._callFor(x, BasePermissions.REMOVED));
    }

    if ('permissions' in permissions) {
      permissions.permissions.forEach(x => this._callFor(x, BasePermissions.REMOVED));
    }
  }
}