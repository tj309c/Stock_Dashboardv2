"""
Advanced Machine Learning Models for Stock Analysis
- Hidden Markov Models (HMMs) for regime detection
- Kernel Methods & Support Vector Machines for prediction
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.kernel_ridge import KernelRidge
from hmmlearn import hmm
import warnings
warnings.filterwarnings('ignore')


class MarketRegimeDetector:
    """
    Hidden Markov Model for detecting market regimes

    Identifies hidden states like:
    - Bull Market (strong uptrend)
    - Bear Market (strong downtrend)
    - High Volatility (choppy/uncertain)
    - Low Volatility (consolidation)
    """

    def __init__(self, n_states=4):
        """
        Args:
            n_states: Number of hidden market regimes (default: 4)
        """
        self.n_states = n_states
        self.model = None
        self.regime_labels = {
            0: "Bull Market",
            1: "Bear Market",
            2: "High Volatility",
            3: "Low Volatility"
        }
        self.regime_colors = {
            0: "🟢",
            1: "🔴",
            2: "🟡",
            3: "⚪"
        }

    def prepare_features(self, price_data):
        """
        Extract features for HMM from price data

        Features:
        - Returns
        - Volatility (rolling std)
        - Volume changes
        - Momentum
        """
        df = price_data.copy()

        # Calculate returns
        df['returns'] = df['Close'].pct_change()

        # Volatility (10-day rolling std)
        df['volatility'] = df['returns'].rolling(window=10).std()

        # Volume changes
        df['volume_change'] = df['Volume'].pct_change()

        # Momentum (5-day rate of change)
        df['momentum'] = df['Close'].pct_change(periods=5)

        # Drop NaN rows
        df = df.dropna()

        # Select features for HMM
        features = df[['returns', 'volatility', 'volume_change', 'momentum']].values

        return features, df.index

    def fit(self, price_data):
        """
        Fit Hidden Markov Model to price data
        """
        features, _ = self.prepare_features(price_data)

        # Create Gaussian HMM
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )

        # Fit the model
        self.model.fit(features)

        return self

    def predict_regimes(self, price_data):
        """
        Predict market regimes for given price data

        Returns:
            DataFrame with regime predictions
        """
        features, dates = self.prepare_features(price_data)

        # Predict hidden states
        hidden_states = self.model.predict(features)

        # Map states to interpretable labels based on characteristics
        state_means = self.model.means_

        # Classify states based on returns and volatility
        regime_mapping = {}
        for state in range(self.n_states):
            avg_return = state_means[state][0]  # returns
            avg_volatility = state_means[state][1]  # volatility

            # Classification logic
            if avg_return > 0 and avg_volatility < np.median(state_means[:, 1]):
                regime_mapping[state] = 0  # Bull Market
            elif avg_return < 0 and avg_volatility < np.median(state_means[:, 1]):
                regime_mapping[state] = 1  # Bear Market
            elif avg_volatility > np.median(state_means[:, 1]):
                regime_mapping[state] = 2  # High Volatility
            else:
                regime_mapping[state] = 3  # Low Volatility

        # Map states to regime labels
        regimes = [regime_mapping.get(state, state) for state in hidden_states]

        # Create result dataframe
        result = pd.DataFrame({
            'date': dates,
            'regime': regimes,
            'regime_name': [self.regime_labels[r] for r in regimes],
            'regime_icon': [self.regime_colors[r] for r in regimes]
        })

        result.set_index('date', inplace=True)

        return result

    def get_transition_probabilities(self):
        """
        Get regime transition probability matrix

        Shows likelihood of transitioning from one regime to another
        """
        if self.model is None:
            return None

        trans_matrix = self.model.transmat_

        # Create labeled dataframe
        regime_names = [self.regime_labels[i] for i in range(self.n_states)]

        trans_df = pd.DataFrame(
            trans_matrix,
            index=regime_names,
            columns=regime_names
        )

        return trans_df


class KernelPredictor:
    """
    Kernel Methods for non-linear pattern recognition and prediction

    Uses Support Vector Machines (SVM) and Kernel Ridge Regression
    to capture complex non-linear relationships in price data
    """

    def __init__(self, kernel='rbf', lookback=20):
        """
        Args:
            kernel: Kernel type ('rbf', 'poly', 'sigmoid')
            lookback: Number of days to use as features
        """
        self.kernel = kernel
        self.lookback = lookback
        self.scaler = StandardScaler()
        self.classifier = None
        self.regressor = None

    def prepare_features(self, price_data):
        """
        Create feature matrix for kernel methods

        Features:
        - Past N days of returns
        - Moving averages
        - RSI
        - MACD
        """
        df = price_data.copy()

        # Calculate returns
        df['returns'] = df['Close'].pct_change()

        # Technical indicators
        df['SMA10'] = df['Close'].rolling(window=10).mean()
        df['SMA20'] = df['Close'].rolling(window=20).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26

        # Create lagged features
        feature_cols = []
        for i in range(1, self.lookback + 1):
            col_name = f'return_lag_{i}'
            df[col_name] = df['returns'].shift(i)
            feature_cols.append(col_name)

        # Add technical indicators
        df['sma_diff'] = (df['SMA10'] - df['SMA20']) / df['SMA20']
        feature_cols.extend(['sma_diff', 'RSI', 'MACD'])

        # Drop NaN rows
        df = df.dropna()

        X = df[feature_cols].values
        y_class = (df['returns'].shift(-1) > 0).astype(int).values  # Next day direction
        y_reg = df['Close'].shift(-1).values  # Next day price

        # Remove last row (no future data)
        X = X[:-1]
        y_class = y_class[:-1]
        y_reg = y_reg[:-1]
        dates = df.index[:-1]

        return X, y_class, y_reg, dates

    def fit_classifier(self, price_data):
        """
        Fit SVM classifier to predict next-day direction (up/down)
        """
        X, y_class, _, _ = self.prepare_features(price_data)

        # Split train/test (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, y_train = X[:split_idx], y_class[:split_idx]

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train SVM classifier
        self.classifier = SVC(
            kernel=self.kernel,
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )

        self.classifier.fit(X_train_scaled, y_train)

        return self

    def fit_regressor(self, price_data):
        """
        Fit Kernel Ridge Regression to predict next-day price
        """
        X, _, y_reg, _ = self.prepare_features(price_data)

        # Split train/test (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, y_train = X[:split_idx], y_reg[:split_idx]

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train Kernel Ridge Regression
        self.regressor = KernelRidge(
            kernel=self.kernel,
            alpha=1.0,
            gamma=None
        )

        self.regressor.fit(X_train_scaled, y_train)

        return self

    def predict(self, price_data):
        """
        Make predictions using trained models

        Returns:
            DataFrame with predictions and probabilities
        """
        X, _, _, dates = self.prepare_features(price_data)

        # Scale features
        X_scaled = self.scaler.transform(X)

        results = pd.DataFrame(index=dates)

        # Classification predictions
        if self.classifier is not None:
            predictions = self.classifier.predict(X_scaled)
            probabilities = self.classifier.predict_proba(X_scaled)

            results['direction'] = predictions
            results['direction_label'] = results['direction'].map({1: 'Up', 0: 'Down'})
            results['up_probability'] = probabilities[:, 1]
            results['confidence'] = np.max(probabilities, axis=1)

        # Regression predictions
        if self.regressor is not None:
            price_predictions = self.regressor.predict(X_scaled)
            results['predicted_price'] = price_predictions

        return results

    def evaluate(self, price_data):
        """
        Evaluate model performance on test set

        Returns:
            Dictionary with accuracy metrics
        """
        X, y_class, y_reg, _ = self.prepare_features(price_data)

        # Split train/test (80/20)
        split_idx = int(len(X) * 0.8)
        X_test, y_test_class, y_test_reg = X[split_idx:], y_class[split_idx:], y_reg[split_idx:]

        # Scale test features
        X_test_scaled = self.scaler.transform(X_test)

        metrics = {}

        # Classification accuracy
        if self.classifier is not None:
            y_pred_class = self.classifier.predict(X_test_scaled)
            accuracy = (y_pred_class == y_test_class).mean()
            metrics['classification_accuracy'] = accuracy

            # Win rate (profitable trades)
            metrics['directional_accuracy'] = f"{accuracy * 100:.1f}%"

        # Regression metrics
        if self.regressor is not None:
            y_pred_reg = self.regressor.predict(X_test_scaled)

            # RMSE
            rmse = np.sqrt(np.mean((y_pred_reg - y_test_reg) ** 2))
            metrics['price_rmse'] = rmse

            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((y_test_reg - y_pred_reg) / y_test_reg)) * 100
            metrics['price_mape'] = f"{mape:.2f}%"

        return metrics


def render_advanced_ml_analysis(ticker, price_data):
    """
    Render advanced ML analysis section with HMMs and Kernel Methods
    """
    st.markdown("### 🤖 Advanced Machine Learning Analysis")
    st.markdown("*Hidden Markov Models & Kernel Methods for regime detection and prediction*")

    # Create tabs for different ML models
    hmm_tab, kernel_tab = st.tabs(["📊 Market Regime Detection (HMM)", "🎯 Kernel Predictions (SVM/KRR)"])

    with hmm_tab:
        st.markdown("#### Hidden Markov Model - Market Regime Detection")
        st.markdown("Identifies hidden market states and predicts regime transitions")

        # HMM parameters
        col1, col2 = st.columns(2)
        with col1:
            n_regimes = st.selectbox("Number of Market Regimes", [3, 4, 5], index=1)

        with col2:
            if st.button("🔍 Detect Market Regimes", type="primary"):
                with st.spinner("Training Hidden Markov Model..."):
                    # Train HMM
                    detector = MarketRegimeDetector(n_states=n_regimes)
                    detector.fit(price_data)

                    # Predict regimes
                    regime_predictions = detector.predict_regimes(price_data)

                    # Display current regime
                    current_regime = regime_predictions.iloc[-1]
                    st.success(f"**Current Market Regime:** {current_regime['regime_icon']} {current_regime['regime_name']}")

                    # Regime statistics
                    st.markdown("#### Regime Statistics")
                    regime_counts = regime_predictions['regime_name'].value_counts()

                    stat_cols = st.columns(min(n_regimes, 4))
                    for idx, (regime, count) in enumerate(regime_counts.items()):
                        with stat_cols[idx % 4]:
                            pct = (count / len(regime_predictions)) * 100
                            st.metric(regime, f"{count} days", f"{pct:.1f}%")

                    # Transition matrix
                    st.markdown("#### Regime Transition Probabilities")
                    st.markdown("*Probability of switching from one regime to another*")

                    trans_matrix = detector.get_transition_probabilities()

                    # Format as percentage
                    trans_matrix_pct = (trans_matrix * 100).round(1).astype(str) + '%'
                    st.dataframe(trans_matrix_pct, use_container_width=True)

                    # Regime timeline
                    st.markdown("#### Recent Regime History (Last 30 Days)")
                    recent_regimes = regime_predictions.tail(30)

                    timeline_df = recent_regimes[['regime_icon', 'regime_name']].copy()
                    timeline_df.index = timeline_df.index.strftime('%Y-%m-%d')
                    timeline_df.columns = ['', 'Market Regime']

                    st.dataframe(timeline_df, use_container_width=True)

                    # Interpretation guide
                    with st.expander("📚 How to Interpret Regimes"):
                        st.markdown("""
                        **Market Regimes Explained:**

                        🟢 **Bull Market**
                        - Strong upward trend with low volatility
                        - Best for long positions and trend following
                        - High probability of continued gains

                        🔴 **Bear Market**
                        - Strong downward trend with low volatility
                        - Consider short positions or staying in cash
                        - High probability of continued losses

                        🟡 **High Volatility**
                        - Choppy, uncertain market conditions
                        - Difficult to predict direction
                        - Use tight stops and smaller positions

                        ⚪ **Low Volatility**
                        - Consolidation phase
                        - Calm before potential breakout
                        - Monitor for regime change signals

                        **Transition Probabilities:**
                        - High diagonal values = stable regimes
                        - High off-diagonal values = frequent regime changes
                        """)

    with kernel_tab:
        st.markdown("#### Kernel Methods - Non-Linear Prediction")
        st.markdown("Support Vector Machines and Kernel Ridge Regression for price prediction")

        # Kernel parameters
        col1, col2, col3 = st.columns(3)

        with col1:
            kernel_type = st.selectbox("Kernel Type", ['rbf', 'poly', 'sigmoid'], index=0)

        with col2:
            lookback_days = st.slider("Feature Lookback", 10, 30, 20)

        with col3:
            prediction_type = st.multiselect(
                "Prediction Type",
                ["Direction (SVM)", "Price (KRR)"],
                default=["Direction (SVM)"]
            )

        if st.button("🎯 Run Kernel Predictions", type="primary"):
            with st.spinner("Training kernel models..."):
                predictor = KernelPredictor(kernel=kernel_type, lookback=lookback_days)

                # Train selected models
                if "Direction (SVM)" in prediction_type:
                    predictor.fit_classifier(price_data)

                if "Price (KRR)" in prediction_type:
                    predictor.fit_regressor(price_data)

                # Make predictions
                predictions = predictor.predict(price_data)

                # Evaluate performance
                metrics = predictor.evaluate(price_data)

                # Display metrics
                st.markdown("#### Model Performance (Test Set)")

                metric_cols = st.columns(len(metrics))
                for idx, (metric_name, metric_value) in enumerate(metrics.items()):
                    with metric_cols[idx]:
                        display_name = metric_name.replace('_', ' ').title()
                        st.metric(display_name, metric_value)

                # Recent predictions
                st.markdown("#### Recent Predictions (Last 10 Days)")

                recent_preds = predictions.tail(10).copy()
                recent_preds.index = recent_preds.index.strftime('%Y-%m-%d')

                # Add actual next-day results for comparison
                actual_prices = price_data['Close'].loc[recent_preds.index]
                recent_preds['actual_price'] = actual_prices.values

                # Format columns
                display_cols = []
                if 'direction_label' in recent_preds.columns:
                    display_cols.extend(['direction_label', 'up_probability', 'confidence'])
                if 'predicted_price' in recent_preds.columns:
                    display_cols.extend(['predicted_price', 'actual_price'])

                if display_cols:
                    display_df = recent_preds[display_cols].copy()

                    # Format percentages
                    if 'up_probability' in display_df.columns:
                        display_df['up_probability'] = (display_df['up_probability'] * 100).round(1).astype(str) + '%'
                    if 'confidence' in display_df.columns:
                        display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'

                    # Format prices
                    if 'predicted_price' in display_df.columns:
                        display_df['predicted_price'] = display_df['predicted_price'].round(2)
                    if 'actual_price' in display_df.columns:
                        display_df['actual_price'] = display_df['actual_price'].round(2)

                    # Rename columns
                    display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]

                    st.dataframe(display_df, use_container_width=True)

                # Interpretation guide
                with st.expander("📚 How to Interpret Kernel Predictions"):
                    st.markdown("""
                    **Kernel Methods Explained:**

                    **Support Vector Machine (SVM) - Direction Prediction:**
                    - Predicts whether next day will be UP or DOWN
                    - **Up Probability**: Likelihood of price increase (>50% = bullish)
                    - **Confidence**: Model's certainty (>70% = high confidence)
                    - **Directional Accuracy**: % of correct up/down predictions

                    **Kernel Ridge Regression (KRR) - Price Prediction:**
                    - Predicts actual next-day closing price
                    - **RMSE**: Root Mean Square Error (lower is better)
                    - **MAPE**: Mean Absolute Percentage Error (lower is better)

                    **Trading Signals:**
                    - ✅ Strong Buy: Direction = Up, Confidence > 70%
                    - ✅ Moderate Buy: Direction = Up, Confidence 50-70%
                    - ❌ Moderate Sell: Direction = Down, Confidence 50-70%
                    - ❌ Strong Sell: Direction = Down, Confidence > 70%

                    **Kernel Types:**
                    - **RBF (Radial Basis Function)**: Best for smooth, non-linear patterns
                    - **Polynomial**: Captures complex polynomial relationships
                    - **Sigmoid**: Similar to neural network decision boundaries
                    """)
