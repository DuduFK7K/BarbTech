import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TelaLoginUsuario } from './tela-login-usuario';

describe('TelaLoginUsuario', () => {
  let component: TelaLoginUsuario;
  let fixture: ComponentFixture<TelaLoginUsuario>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TelaLoginUsuario],
    }).compileComponents();

    fixture = TestBed.createComponent(TelaLoginUsuario);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
