import * as THREE from 'three';

export async function loadPolicies() {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}data/policies.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const ids = ['home', 'tree', 'temple', 'koi', 'meadow', 'windmill', 'crystal', 'lookout'];
    if (!Array.isArray(data.policies) || data.policies.length !== 8 ||
        ids.some((id) => data.policies.filter((p) => p.id === id).length !== 1) ||
        data.policies.some((p) => typeof p.name !== 'string' || !p.name.trim() ||
          (p.introduction !== null && typeof p.introduction !== 'string') ||
          !Array.isArray(p.items) || p.items.some((item) => typeof item !== 'string'))) {
      throw new Error('政策 JSON 格式不正確');
    }
    return data;
  } catch (error) {
    document.querySelector('#loading p').textContent = '政策資料載入失敗，請檢查 policies.json 後重新整理。';
    throw error;
  }
}

export class PolicyUI {
  constructor(data, islands, camera, ui) {
    this.policies = new Map(data.policies.map((policy) => [policy.id, policy]));
    this.camera = camera;
    this.ui = ui;
    this.dialog = document.getElementById('policy-dialog');
    this.labels = [];
    const labels = document.getElementById('island-labels');
    const list = document.getElementById('policy-list');
    for (const island of islands) {
      const policy = this.policies.get(island.name);
      const makeButton = () => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = policy.name;
        button.setAttribute('aria-haspopup', 'dialog');
        button.addEventListener('click', () => this.open(policy.id));
        return button;
      };
      list.append(makeButton());
      const label = makeButton();
      label.className = `island-label${island.name === 'home' ? ' home-policy' : ''}`;
      label.dataset.island = island.name;
      labels.append(label);
      this.labels.push({ element: label, island, position: island.pos.clone().add(new THREE.Vector3(0, 2.5, 0)) });
    }
    document.getElementById('policy-close').addEventListener('click', () => this.dialog.close());
    this.dialog.addEventListener('click', (event) => {
      const rect = this.dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) this.dialog.close();
    });
    this.dialog.addEventListener('close', () => {
      const menu = document.getElementById('policy-menu');
      const target = this.previousFocus?.closest('#policy-list') ? menu.querySelector('summary') : this.previousFocus;
      if (target?.isConnected) target.focus();
    });
  }

  get isOpen() { return this.dialog.open; }

  open(id) {
    const policy = this.policies.get(id);
    if (!policy || this.isOpen) return;
    this.previousFocus = document.activeElement;
    document.getElementById('policy-title').textContent = policy.name;
    const content = document.getElementById('policy-content');
    content.replaceChildren();
    if (policy.introduction?.trim()) {
      const p = document.createElement('p');
      p.textContent = policy.introduction;
      content.append(p);
    }
    if (policy.items.length) {
      const list = document.createElement('ul');
      for (const item of policy.items) {
        const li = document.createElement('li');
        li.textContent = item;
        list.append(li);
      }
      content.append(list);
    }
    if (!content.childElementCount) {
      const p = document.createElement('p');
      p.className = 'empty-policy';
      p.textContent = '政策內容尚未提供，待補充。';
      content.append(p);
    }
    if (id === 'home') {
      const note = document.createElement('p');
      note.textContent = '場景設施為政策主題示意，不代表實際工程已核定或完成。';
      content.append(note);
    }
    this.ui._keys.clear();
    Object.assign(this.ui.input, { x: 0, z: 0, jumpPressed: false, jumpHeld: false });
    document.getElementById('policy-menu').open = false;
    this.dialog.showModal();
  }

  update(started, playerPosition) {
    document.getElementById('policy-nav').hidden = !started;
    for (const label of this.labels) {
      const anchor = label.position.clone();
      // Keep the current island's sign near the explorer on narrow screens.
      // Distant island signs remain anchored to their island centres.
      if (Math.hypot(playerPosition.x - label.island.pos.x, playerPosition.z - label.island.pos.z) < label.island.r &&
          Math.abs(playerPosition.y - label.island.pos.y) < 4) {
        anchor.x = THREE.MathUtils.lerp(anchor.x, playerPosition.x, 0.8);
        anchor.z = THREE.MathUtils.lerp(anchor.z, playerPosition.z, 0.8);
      }
      const p = anchor.project(this.camera);
      const visible = started && p.z > -1 && p.z < 1 && Math.abs(p.x) < 0.92 && Math.abs(p.y) < 0.9;
      label.element.hidden = !visible;
      if (visible) {
        label.element.style.left = `${(p.x + 1) * 50}%`;
        label.element.style.top = `${(1 - p.y) * 50}%`;
      }
    }
  }
}
