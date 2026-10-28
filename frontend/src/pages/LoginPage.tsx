import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../services/authService";

import "../styles/login.css";

export default function LoginPage() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  const handleLogin = async () => {

    try {

      setError("");

      const data = await login(
        email,
        password
      );

      localStorage.setItem(
        "token",
        data.access_token
      );

      navigate("/upload");

    } catch {

      setError(
        "Usuario o contraseña incorrectos"
      );
    }
  };

  return (

    <div className="login-page">

      <div className="login-card">

        <h1>
          Sistema de Digitalización de Documentos
        </h1>

        <p>
          Instituto Nacional de Enfermedades Neoplásicas (INEN)
        </p>

        <div className="form-group">

          <label>Usuario</label>

          <input
            type="text"
            placeholder="Ingrese su usuario"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />

        </div>

        <div className="form-group">

          <label>Contraseña</label>

          <input
            type="password"
            placeholder="Ingrese su contraseña"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />

        </div>

        {
          error &&
          (
            <p
              style={{
                color: "red",
                marginBottom: "15px"
              }}
            >
              {error}
            </p>
          )
        }

        <button
          className="login-button"
          onClick={handleLogin}
        >
          Iniciar sesión
        </button>

      </div>

    </div>
  );
}