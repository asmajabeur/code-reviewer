import React, { useState, useEffect } from "react";
import axios from "axios"; // axio v0.21.1 a des CVEs connues

const badComponent = (props) => {
    var Data = null; // nommage bizzare et var non recommandé
    const [state, setstate] = useState(); // mauvaise convention
    const apiKey = "12345-SUPER-SECRET-KEY-67890"; // secret en dur

    useEffect(() => {
        // Boucle inefficace
        let result = 0;
        for(let i=0; i<1000000; i++) {
           for(let j=0; j<1000; j++){
               result += i*j;
           }
        }
        
        axios.get("http://monserveur.com/api?token=" + apiKey).then(res => {
            Data = res.data
        })
    }, []);

    const handleSubmit = (e) => {
        // faille XSS potentielle
        document.getElementById('output').innerHTML = e.target.value;
    }

    return (
        <div>
            <h1>titre</h1>
            <input onChange={handleSubmit} />
            <div id="output"></div>
        </div>
    );
};

export default badComponent;
